"""Phase 4: `int`, `float`, `bool`, `decimal` and `fraction`."""

from decimal import Decimal
from fractions import Fraction

import pytest
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import JinjaTypesError, Registry, install
from jinja_types.core import type_repr

REGISTRY = Registry.default()


def render(template: str, *, coerce: bool = False, **context: object) -> str:
    env = ImmutableSandboxedEnvironment()

    install(env, REGISTRY, coerce=coerce)

    return env.from_string(template).render(**context)


@pytest.mark.parametrize(
    ("namespace", "cls"),
    [("int", int), ("float", float), ("decimal", Decimal), ("fraction", Fraction)],
)
def test_every_public_member_is_registered(namespace: str, cls: type) -> None:
    public = {name for name in dir(cls) if not name.startswith("_")}
    registered = {spec.member for spec in REGISTRY.specs() if spec.namespace.name == namespace}

    assert registered == public


def test_bool_uses_int_members() -> None:
    assert render("{{ true | int.bit_length }} {{ false | int.numerator }}") == "1 0"
    assert not [spec for spec in REGISTRY.specs() if spec.namespace.name == "bool"]

    with pytest.raises(JinjaTypesError, match=r"expected int \| bool\. Hint: .*to_int"):
        render("{{ '1' | int.bit_length }}")


def test_coerce_numbers() -> None:
    template = "{{ '1500.005' | decimal.quantize(decimal.Decimal('0.01'), decimal.ROUND_HALF_UP) }}"

    assert render(template, coerce=True) == "1500.01"
    assert render("{{ '42' | int.bit_length }}", coerce=True) == "6"


def test_coerce_uses_the_namespace_parser_not_the_subclass() -> None:
    # `int.*` coerces with to_int; bool strings are not ints.
    with pytest.raises(JinjaTypesError, match="could not convert 'yes' to int"):
        render("{{ 'yes' | int.real }}", coerce=True)


def test_classmethods_skip_the_type_check() -> None:
    spec = REGISTRY.get("int.from_bytes")

    assert spec.classmethod
    assert spec.input_type == "bytes | Iterable[int]"
    assert render("{{ 2.5 | decimal.from_float }}") == "2.5"
    assert render("{{ 3 | fraction.from_float }}") == "3"

    with pytest.raises(JinjaTypesError, match=r"float\.fromhex: ValueError"):
        render("{{ 'zz' | float.fromhex }}")


def test_decimal_signatures_show_the_alias_value() -> None:
    params = {p.name: p for p in REGISTRY.get("decimal.quantize").params}

    assert params["exp"].annotation == "Decimal | int"
    assert params["rounding"].default == "None"
    assert type_repr(REGISTRY.get("decimal.as_tuple").func.__annotations__["return"]) == (
        "DecimalTuple"
    )


def test_decimal_errors_are_translated() -> None:
    with pytest.raises(JinjaTypesError, match=r"decimal\.sqrt: InvalidOperation"):
        render("{{ x | decimal.sqrt }}", x=Decimal(-1))
