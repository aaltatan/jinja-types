"""Core behaviour: dispatch, conflicts, options, errors and hints, plugins, install."""

from collections.abc import Callable, Mapping
from datetime import date, datetime
from decimal import Decimal
from importlib.metadata import EntryPoint
from typing import Literal, Unpack

import demo
import pytest
from jinja2 import Environment, TemplateRuntimeError, UndefinedError
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import (
    BuiltinClashError,
    Collection,
    DuplicateMemberError,
    JinjaTypesError,
    Kind,
    Options,
    Registry,
    RegistryError,
    TypesExtension,
    install,
)
from jinja_types.core import PLUGIN_GROUP, OptionsKwargs, plugins, type_repr

NAMESPACES = [
    "bool",
    "date",
    "datetime",
    "decimal",
    "dict",
    "float",
    "fraction",
    "int",
    "list",
    "match",
    "re",
    "str",
    "time",
    "timedelta",
]


def render(
    template: str,
    registry: Registry | None = None,
    /,
    context: Mapping[str, object] | None = None,
    **options: Unpack[OptionsKwargs],
) -> str:
    env = ImmutableSandboxedEnvironment()

    install(env, registry or demo.demo_registry(), **options)

    return env.from_string(template).render(**(context or {}))


def labelled() -> Registry:
    """`date.label` and `datetime.label` return their namespace name, to make dispatch visible."""

    base = Collection("date", date)
    child = Collection("datetime", datetime)

    @base.filter()
    def label(value: date, /) -> str:
        """Label."""
        return "date"

    @base.filter()
    def shared(value: date, /) -> str:
        """Only on the parent."""
        return "parent"

    @child.filter(member="label")
    def label_dt(value: datetime, /) -> str:
        """Label."""
        return "datetime"

    return Registry().include(base, child)


# --- rendering and dispatch ------------------------------------------------------------------


def test_dotted_filters_tests_and_globals_render_in_sandbox() -> None:
    assert render("{{ d | date.year }}", context={"d": demo.DAY}) == "2026"
    assert render("{% if 4 is is_even %}yes{% endif %}") == "yes"
    assert render("{{ answer() }}") == "42"


def test_dispatch_picks_the_subclass_member() -> None:
    registry = labelled()

    assert render("{{ d | date.label }}", registry, context={"d": demo.MOMENT}) == "datetime"
    assert render("{{ d | date.label }}", registry, context={"d": demo.DAY}) == "date"
    assert render("{{ d | date.shared }}", registry, context={"d": demo.MOMENT}) == "parent"


def test_child_namespace_rejects_parent_values() -> None:
    with pytest.raises(JinjaTypesError, match=r"datetime\.label: got 'date', expected datetime"):
        render("{{ d | datetime.label }}", labelled(), context={"d": demo.DAY})


def test_unrelated_namespace_with_same_type_is_not_dispatched_to() -> None:
    text = Collection("str", str)
    module = Collection("re", str)

    @text.filter()
    def split(value: str, /) -> str:
        """str.split."""
        return "str"

    @module.filter(member="split")
    def re_split(value: str, /) -> str:
        """re.split."""
        return "re"

    registry = Registry().include(text, module)

    assert render("{{ 'a' | str.split }} {{ 'a' | re.split }}", registry) == "str re"


# --- errors and hints ------------------------------------------------------------------------


def test_wrong_type_error_has_hint_and_fields() -> None:
    with pytest.raises(JinjaTypesError) as info:
        render("{{ '2026-01-05' | date.strftime('%Y') }}")

    error = info.value

    assert str(error) == (
        "date.strftime: got 'str', expected date | datetime. "
        "Hint: convert first with '| to_date' or '| date.fromisoformat'."
    )
    assert isinstance(error, TemplateRuntimeError)
    assert error.filter_name == "date.strftime"
    assert error.value_type == "str"
    assert error.supported == ("date", "datetime")


def test_wrong_type_hint_for_unknown_namespace() -> None:
    other = Collection("money", Decimal)

    @other.attribute()
    def real(value: Decimal, /) -> Decimal:
        """Real part."""
        return value.real

    with pytest.raises(JinjaTypesError, match="Hint: pass a Decimal value"):
        render("{{ 1 | money.real }}", Registry().include(other))


def test_exceptions_are_translated_with_cause() -> None:
    with pytest.raises(JinjaTypesError) as info:
        render("{{ d | date.strftime(1) }}", context={"d": demo.DAY})

    error = info.value

    assert isinstance(error.original, TypeError)
    assert error.__cause__ is error.original
    assert error.hint == "check the arguments: date.strftime(format: str)"


def test_non_type_errors_have_no_hint() -> None:
    helpers = Collection()

    @helpers.filter()
    def explode(value: int, /, scale: int = 2) -> int:
        """Divide by zero."""
        return value // 0

    @helpers.global_()
    def boom() -> int:
        """Fail."""
        raise ValueError("nope")

    registry = Registry().include(helpers)

    with pytest.raises(JinjaTypesError, match=r"^explode: ZeroDivisionError: .*\.$") as info:
        render("{{ 1 | explode }}", registry)

    assert info.value.hint is None
    assert info.value.value_type == "int"

    with pytest.raises(JinjaTypesError, match="boom: ValueError: nope") as info:
        render("{{ boom() }}", registry)

    assert info.value.value_type is None


def test_jinja_errors_pass_through_untouched() -> None:
    helpers = Collection()

    @helpers.filter()
    def call_it(value: int, macro: Callable[[], object], /) -> str:
        """Call a macro."""
        return str(macro())

    template = "{% macro m() %}{{ missing.attr }}{% endmacro %}{{ 1 | call_it(m) }}"

    with pytest.raises(UndefinedError):
        render(template, Registry().include(helpers))


# --- options ---------------------------------------------------------------------------------


@pytest.mark.parametrize(("value", "label"), [(None, "None"), ("", "an empty string")])
def test_strict_by_default(value: object, label: str) -> None:
    with pytest.raises(JinjaTypesError, match=f"got {label}.*none_passthrough=True"):
        render("{{ x | date.year }}", context={"x": value})

    with pytest.raises(JinjaTypesError, match=f"shout: got {label}"):
        render("{{ x | shout }}", context={"x": value})


def test_undefined_is_missing() -> None:
    with pytest.raises(JinjaTypesError, match="got an undefined value"):
        render("{{ nope | date.year }}")


def test_none_passthrough() -> None:
    template = "[{{ x | date.year }}][{{ y | date.year }}][{{ nope | shout }}][{{ x is is_even }}]"

    context = {"x": None, "y": ""}

    assert render(template, context=context, none_passthrough=True) == "[None][][][False]"


def test_coerce_parses_strings() -> None:
    assert render("{{ '2026-01-05' | date.year }}", coerce=True) == "2026"


def test_coerce_parse_failure() -> None:
    with pytest.raises(JinjaTypesError, match=r"could not convert 'nope' to date.*to_date") as info:
        render("{{ 'nope' | date.year }}", coerce=True)

    assert isinstance(info.value.original, ValueError)


def test_coerce_without_parse_still_rejects() -> None:
    with pytest.raises(JinjaTypesError, match="got 'str', expected list"):
        render("{{ 'ab' | list.append(1) }}", coerce=True)


def test_options_defaults() -> None:
    expected = Options(none_passthrough=False, coerce=False, regex_timeout=1.0, locale=None)

    assert Options() == expected


# --- conflicts -------------------------------------------------------------------------------


def test_duplicate_name_raises_and_leaves_registry_unchanged() -> None:
    registry = Registry().include(demo.date_ns)
    again = Collection("date", date)

    @again.attribute()
    def year(value: date, /) -> int:
        """Year."""
        return 0

    fresh = Collection("fresh", int)

    @fresh.attribute()
    def real(value: int, /) -> int:
        """Real."""
        return value

    with pytest.raises(DuplicateMemberError, match=r"date\.year is already registered"):
        registry.include(fresh, again)

    assert "fresh.real" not in registry
    assert registry.get("date.year").func is demo.year


def test_replace_is_recorded() -> None:
    plugin = Collection("date", date)

    @plugin.attribute(member="year")
    def other_year(value: date, /) -> int:
        """Year, differently."""
        return 1

    registry = Registry().include(demo.date_ns).include(plugin, replace=True, source="acme")
    spec = registry.get("date.year")
    entry = next(e for e in registry.catalog() if e.name == "date.year")

    assert spec.func is other_year
    assert (spec.source, spec.replaced) == ("acme", True)
    assert (entry.source, entry.replaced) == ("acme", True)
    assert [(c.name, c.resolution, c.detail) for c in registry.conflicts()] == [
        ("date.year", "replaced", "jinja_types replaced by acme")
    ]


def test_replace_without_existing_is_not_a_conflict() -> None:
    registry = Registry().include(demo.date_ns, replace=True)

    assert registry.conflicts() == []
    assert not registry.get("date.year").replaced


def test_parent_and_child_members_are_both_kept() -> None:
    registry = labelled()

    assert {"date.label", "datetime.label"} <= {spec.name for spec in registry.specs()}
    assert [(c.name, c.resolution) for c in registry.conflicts()] == [
        ("datetime.label", "dispatch")
    ]


def test_namespace_type_mismatch() -> None:
    with pytest.raises(RegistryError, match="bound to date, not int"):
        Registry().include(demo.date_ns, Collection("date", int))


def test_namespace_parse_is_kept_or_filled() -> None:
    registry = Registry().include(Collection("date", date))

    assert registry.namespace("date").parse is None

    registry.include(demo.date_ns).include(Collection("date", date))

    assert registry.namespace("date").parse == date.fromisoformat


def test_duplicate_within_a_collection() -> None:
    collection = Collection()

    @collection.filter()
    def twice(value: int, /) -> int:
        """Once."""
        return value

    def again(value: int, /) -> int:
        return value

    with pytest.raises(DuplicateMemberError, match="defined twice"):
        collection.filter(member="twice")(again)


@pytest.mark.parametrize(
    ("kind", "name"), [("filter", "upper"), ("test", "even"), ("global", "range")]
)
def test_builtin_clash(kind: str, name: str) -> None:
    helpers = Collection()

    def clash(value: int, /) -> bool:
        """Clash."""
        return True

    def clash_global() -> int:
        """Clash."""
        return 1

    match kind:
        case "filter":
            helpers.filter(member=name, test=False)(clash)
        case "test":
            helpers.test(member=name)(clash)
        case _:
            helpers.global_(member=name)(clash_global)

    env = Environment()
    before = dict(env.filters)

    with pytest.raises(BuiltinClashError, match=f"'{name}' clashes with the existing Jinja {kind}"):
        install(env, Registry().include(helpers, demo.date_ns))

    assert env.filters == before


def test_reinstall_is_not_a_clash() -> None:
    env = Environment()
    registry = demo.demo_registry()

    install(env, registry)
    install(env, registry)

    assert env.from_string("{{ 'a' | shout }}").render() == "A!"


# --- collections and specs -------------------------------------------------------------------


def test_missing_annotations() -> None:
    def untyped(value, /):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202
        return value

    with pytest.raises(RegistryError, match="missing annotations for value, return"):
        Collection().filter()(untyped)


def test_unresolvable_annotations() -> None:
    def broken(value: "Nope", /) -> int:  # type: ignore[name-defined]  # noqa: F821
        return 1

    with pytest.raises(RegistryError, match="cannot resolve type hints"):
        Collection().filter()(broken)


def test_value_must_be_positional_only() -> None:
    def keyword(value: int) -> int:
        return value

    with pytest.raises(RegistryError, match="must be positional-only"):
        Collection().filter()(keyword)


def test_attribute_takes_no_arguments() -> None:
    def attr(value: int, /, extra: int) -> int:
        return value

    with pytest.raises(RegistryError, match="takes no arguments"):
        Collection("int", int).attribute()(attr)


def test_global_needs_helper_namespace() -> None:
    def g() -> int:
        return 1

    with pytest.raises(RegistryError, match="globals belong in the helper namespace"):
        Collection("int", int).global_()(g)


def test_spec_fields() -> None:
    spec = demo.demo_registry().get("is_even")

    assert spec.kinds == Kind.FILTER | Kind.TEST
    assert (spec.namespace.name, spec.member, spec.input_type, spec.returns) == (
        None,
        "is_even",
        "int",
        "bool",
    )
    assert repr(demo.helpers) == "Collection(None, 3 members)"
    assert len(demo.helpers) == 3


def test_explicit_test_flag_and_test_only() -> None:
    collection = Collection("re", str)

    @collection.filter(test=True)
    def search(value: str, pattern: str, /) -> str | None:
        """Search."""
        return value if pattern in value else None

    @collection.test()
    def blank(value: str, /) -> bool:
        """Blank test only."""
        return not value.strip()

    registry = Registry().include(collection)

    assert registry.get("re.search").kinds == Kind.FILTER | Kind.TEST
    assert registry.get("re.blank").kinds == Kind.TEST
    assert render("{{ 'abc' is re.search('b') }} {{ 'abc' is re.search('z') }}", registry) == (
        "True False"
    )
    assert render("{{ ' ' is re.blank }}", registry) == "True"


def test_param_defaults_and_kinds() -> None:
    collection = Collection()

    @collection.filter()
    def pad(value: str, /, width: int = 3, *, fill: str | None = None) -> str:
        """Pad."""
        return value.ljust(width, fill or " ")

    params = Registry().include(collection).get("pad").params

    assert [(p.name, p.kind, p.annotation, p.default) for p in params] == [
        ("width", "positional_or_keyword", "int", "3"),
        ("fill", "keyword_only", "str | None", "None"),
    ]


@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        (int, "int"),
        (None, "None"),
        (str | None, "str | None"),
        (list[int], "list[int]"),
        (dict[str, Decimal], "dict[str, Decimal]"),
        (Callable[[int], str], "Callable[[int], str]"),
        (Callable[..., str], "Callable[..., str]"),
        (Literal["a", 1], "Literal['a', 1]"),
        (Mapping, "Mapping"),
    ],
)
def test_type_repr(hint: object, expected: str) -> None:
    assert type_repr(hint) == expected


# --- registry API ----------------------------------------------------------------------------


def test_registry_lookup_and_copy() -> None:
    registry = demo.demo_registry()
    copied = registry.copy()

    copied.include(Collection("extra", int))

    demo_names = NAMESPACES

    assert [ns.name for ns in registry.namespaces()] == demo_names
    assert [ns.name for ns in copied.namespaces()] == sorted([*demo_names, "extra"])
    assert render("{{ d | date.year }}", copied, context={"d": demo.MOMENT}) == "2026"

    with pytest.raises(KeyError):
        registry.get("date.nope")


def test_default_registry_namespaces() -> None:
    assert [ns.name for ns in Registry.default().namespaces()] == NAMESPACES


# --- plugins ---------------------------------------------------------------------------------


def fake_entry_points(*entries: tuple[str, str]) -> Callable[..., list[EntryPoint]]:
    def entry_points(*, group: str) -> list[EntryPoint]:
        return [EntryPoint(name, value, group) for name, value in entries]

    return entry_points


def test_plugin_loading(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        plugins,
        "entry_points",
        fake_entry_points(("zeta", "demo:helpers"), ("alpha", "demo:date_ns")),
    )

    registry = Registry()

    assert plugins.load_plugins(registry) == ["alpha", "zeta"]
    assert registry.get("date.year").source == "alpha"


def test_plugin_loaded_by_default_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(plugins, "entry_points", fake_entry_points(("acme", "demo:collections")))

    registry = Registry.default(plugins=True)

    assert render("{{ 'x' | shout }}", registry) == "X!"
    assert registry.get("shout").source == "acme"


@pytest.mark.parametrize("value", ["demo:DAY", "demo:bad_plugin"])
def test_bad_plugin(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setattr(plugins, "entry_points", fake_entry_points(("bad", value)))

    with pytest.raises(RegistryError, match="plugin 'bad' must provide a Collection"):
        Registry().load_plugins()


def test_plugin_group_name() -> None:
    assert PLUGIN_GROUP == "jinja_types.plugins"


# --- extension -------------------------------------------------------------------------------


def test_extension_configure() -> None:
    extension = TypesExtension.configure(registry=demo.demo_registry(), coerce=True)
    env = ImmutableSandboxedEnvironment(extensions=[extension])

    assert issubclass(extension, TypesExtension)
    assert extension.options == Options(coerce=True)
    assert env.from_string("{{ '2026-01-05' | date.year }}").render() == "2026"


def test_extension_defaults() -> None:
    env = ImmutableSandboxedEnvironment(extensions=[TypesExtension])

    assert env.from_string("{{ 1 }}").render() == "1"
