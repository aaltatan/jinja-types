"""Phase 2: helpers, converters as namespace parsers, and globals."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from fractions import Fraction
from pathlib import PurePath
from typing import Unpack
from uuid import UUID

import pytest
from jinja2 import Environment
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import Collection, JinjaTypesError, Registry, RegistryError, install
from jinja_types.core import OptionsKwargs
from jinja_types.helpers import PARSERS, convert


def render(
    template: str,
    registry: Registry | None = None,
    /,
    **options: Unpack[OptionsKwargs],
) -> str:
    env = ImmutableSandboxedEnvironment()

    install(env, registry, **options)

    return env.from_string(template).render(x=None, empty="")


def test_acceptance() -> None:
    assert render('{{ "1500.5" | to_decimal | fmt(",.2f") }}') == "1,500.50"
    assert render('{{ "05/01/2026" | to_date(format="%d/%m/%Y") | fmt("%A") }}') == "Monday"


def test_no_helper_is_a_jinja_builtin() -> None:
    names = {spec.name for spec in Registry.default().specs()}

    env = Environment()

    assert not names & (env.filters.keys() | env.tests.keys() | env.globals.keys())

    install(env)


def test_globals_survive_reinstall_and_coexist_with_filters() -> None:
    env = ImmutableSandboxedEnvironment()
    registry = Registry.default()
    quantize = Collection("decimal", Decimal)

    @quantize.filter()
    def scale(value: Decimal, /) -> Decimal:
        """Scale."""
        return value * 2

    registry.include(quantize)
    install(env, registry)
    install(env, registry)

    assert env.from_string("{{ decimal.Decimal('1.5') | decimal.scale }}").render() == "3.0"


def test_globals_are_sandbox_safe() -> None:
    assert render("{{ decimal.__class__ }}") == ""
    assert render("{{ re.compile }}") == ""
    assert render("{{ decimal }} {{ re }}") == "<jinja_types decimal> <jinja_types re flags>"


def test_constant_global_must_take_no_arguments() -> None:
    def factory(x: int) -> int:
        return x

    with pytest.raises(RegistryError, match="no-argument factory"):
        Collection().global_(constant=True)(factory)


# --- converters -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("template", "message"),
    [
        ("{{ 'maybe' | to_bool }}", "cannot convert 'maybe' to bool"),
        ("{{ 2 | to_bool }}", "only 0 and 1"),
        ("{{ 'abc' | to_int }}", "ValueError"),
        ("{{ 'abc' | to_decimal }}", "InvalidOperation"),
        ("{{ '2026-13-01' | to_date }}", "ValueError"),
        ("{{ 'nope' | to_timedelta }}", "ValueError"),
        ("{{ 'not-a-uuid' | to_uuid }}", "ValueError"),
    ],
)
def test_converter_errors(template: str, message: str) -> None:
    with pytest.raises(JinjaTypesError, match=message):
        render(template)


def test_converters_directly() -> None:
    assert convert.to_bool(" TRUE ") is True
    assert convert.to_bool(False) is False
    assert convert.to_decimal(Decimal("2")) == Decimal("2")
    assert convert.to_date(date(2026, 1, 5)) == date(2026, 1, 5)
    assert convert.to_date("2026-01-05") == date(2026, 1, 5)
    assert convert.to_datetime(datetime(2026, 1, 5, 9)) == datetime(2026, 1, 5, 9)
    assert convert.to_time(time(9, 30)) == time(9, 30)
    assert convert.to_time("09:30:15") == time(9, 30, 15)
    assert convert.to_timedelta(timedelta(days=1), hours=1) == timedelta(days=1, hours=1)
    assert convert.to_timedelta("90.5") == timedelta(seconds=90.5)
    assert convert.to_timedelta("-1 day, 23:59:59") == timedelta(seconds=-1)
    assert convert.to_timedelta("0:00:01.5") == timedelta(seconds=1.5)
    uuid = UUID("12345678-1234-5678-1234-567812345678")
    assert convert.to_uuid(uuid) is uuid


# --- options with the converters as parsers ---------------------------------------------------

UUID_TEXT = "12345678-1234-5678-1234-567812345678"
PARSE_CASES = [
    ("str", str, "abc", "abc"),
    ("int", int, "42", 42),
    ("float", float, "2.5", 2.5),
    ("bool", bool, "yes", True),
    ("decimal", Decimal, "1.50", Decimal("1.50")),
    ("fraction", Fraction, "3/4", Fraction(3, 4)),
    ("date", date, "2026-01-05", date(2026, 1, 5)),
    ("datetime", datetime, "2026-01-05T09:30", datetime(2026, 1, 5, 9, 30)),
    ("time", time, "09:30", time(9, 30)),
    ("timedelta", timedelta, "90", timedelta(seconds=90)),
    ("uuid", UUID, UUID_TEXT, UUID(UUID_TEXT)),
    ("path", PurePath, "a/b", PurePath("a/b")),
]


def test_every_builtin_namespace_has_a_parser() -> None:
    assert sorted(PARSERS) == sorted(name for name, *_ in PARSE_CASES)


def identity_registry(name: str, cls: type) -> Registry:
    collection = Collection(name, cls, parse=PARSERS[name])

    @collection.attribute(member="repr")
    def repr_(value: object, /) -> str:
        """Return repr(value)."""
        return repr(value)

    return Registry().include(collection)


@pytest.mark.parametrize(("name", "cls", "text", "expected"), PARSE_CASES)
def test_coerce_modes(name: str, cls: type, text: str, expected: object) -> None:
    registry = identity_registry(name, cls)
    template = f"{{{{ {text!r} | {name}.repr }}}}"

    assert render(template, registry, coerce=True) == repr(expected)

    if name != "str":
        with pytest.raises(JinjaTypesError, match=f"got 'str', expected {cls.__name__}"):
            render(template, registry)


@pytest.mark.parametrize("value", ["x", "empty"])
def test_none_passthrough_on_helpers(value: str) -> None:
    template = f"[{{{{ {value} | to_int }}}}]"

    assert render(template, none_passthrough=True) == ("[None]" if value == "x" else "[]")

    with pytest.raises(JinjaTypesError, match="none_passthrough=True"):
        render(template)
