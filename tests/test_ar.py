"""Phase 11: the `ar` namespace (arapy)."""

from decimal import Decimal

import arapy._extras
import pytest
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import JinjaTypesError, Kind, Registry, install
from jinja_types.types.ar_ import SYP

REGISTRY = Registry.default()


def render(template: str, **context: object) -> str:
    env = ImmutableSandboxedEnvironment(autoescape=True)

    install(env, REGISTRY)

    return env.from_string(template).render(**context)


def test_ar_is_built_in() -> None:
    members = {spec.member for spec in REGISTRY.specs() if spec.namespace.name == "ar"}

    assert {"to_words", "format_money", "to_arabic_digits", "format_date", "shape"} <= members
    assert REGISTRY.get("ar.equals").kinds == Kind.FILTER | Kind.TEST
    assert REGISTRY.get("ar.to_words").source == "jinja_types"


def test_phase_example() -> None:
    template = "{{ salary | ar.to_words(syp) }} ({{ salary | ar.format_money(syp) }})"

    assert render(template, salary=Decimal("1500"), syp=SYP) == (
        "ألف وخمسمئة ليرة سورية (١٬٥٠٠ ل.س)"
    )


def test_sort_with_a_macro_key() -> None:
    template = (
        "{% macro first(p) %}{{ p.first }}{% endmacro %}"
        "{{ people | ar.sort(key=first) | map(attribute='age') | join('|') }}"
    )
    people = [{"first": "مريم", "age": 30}, {"first": "أحمد", "age": 41}]

    assert render(template, people=people) == "41|30"


def test_arapy_errors_are_translated() -> None:
    with pytest.raises(JinjaTypesError, match=r"ar\.ordinal: OutOfRangeError"):
        render("{{ 500 | ar.ordinal }}")

    with pytest.raises(JinjaTypesError, match=r"ar\.ordinal: ValueError: 'neuter'"):
        render("{{ 3 | ar.ordinal('neuter') }}")

    with pytest.raises(JinjaTypesError, match=r"ar\.format_money: InvalidNumberError"):
        render("{{ x | ar.format_money(syp) }}", x=Decimal("1.234"), syp=SYP)


def test_missing_extra_hint(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing(name: str) -> object:
        raise ImportError(name)

    monkeypatch.setattr(arapy._extras, "import_module", missing)

    with pytest.raises(JinjaTypesError, match=r"Hint: install 'jinja-types\[shape\]'"):
        render("{{ 'سلام' | ar.shape }}")

    with pytest.raises(JinjaTypesError, match=r"Hint: install 'jinja-types\[hijri\]'"):
        render("{{ d | ar.to_hijri }}", d=__import__("datetime").date(2026, 1, 5))
