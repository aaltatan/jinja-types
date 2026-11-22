"""Phase 10: the `[babel]` extra."""

import importlib
import sys
from decimal import Decimal

import pytest
from jinja2.sandbox import ImmutableSandboxedEnvironment

import jinja_types.types as types_init
from jinja_types import JinjaTypesError, Registry, install

pytest.importorskip("babel")

REGISTRY = Registry.default()
AMOUNT = Decimal("1234.5")


def render(template: str, locale: str | None = None, **context: object) -> str:
    env = ImmutableSandboxedEnvironment()

    install(env, REGISTRY, locale=locale)

    return env.from_string(template).render(**context)


def test_locale_comes_from_the_call_then_the_options_then_en_us() -> None:
    template = "{{ x | babel.format_decimal }}|{{ x | babel.format_decimal(locale='en_US') }}"

    assert render(template, x=AMOUNT) == "1,234.5|1,234.5"
    assert render(template, locale="de_DE", x=AMOUNT) == "1.234,5|1,234.5"


def test_documented_currency_examples() -> None:
    template = "{{ x | babel.format_currency('SYP', locale='ar_SY', currency_digits=false) }}"

    assert render(template, x=AMOUNT) == "‏1,234.50\xa0ل.س.‏"
    assert render("{{ x | babel.format_currency('USD') }}", locale="en_US", x=AMOUNT) == "$1,234.50"


def test_errors_are_translated() -> None:
    with pytest.raises(JinjaTypesError, match=r"babel\.format_decimal: InvalidOperation"):
        render("{{ 'abc' | babel.format_decimal }}")

    with pytest.raises(JinjaTypesError, match=r"babel\.format_currency: UnknownLocaleError"):
        render("{{ 1 | babel.format_currency('USD', locale='xx_XX') }}")

    with pytest.raises(JinjaTypesError, match="got None"):
        render("{{ none | babel.format_date }}")


def test_missing_babel(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(types_init, "find_spec", lambda name: None)

    assert "babel" not in {ns.name for ns in Registry.default().namespaces()}

    monkeypatch.setitem(sys.modules, "babel", None)
    monkeypatch.delitem(sys.modules, "jinja_types.contrib.babel")

    with pytest.raises(ImportError, match=r"install 'jinja-types\[babel\]'"):
        importlib.import_module("jinja_types.contrib.babel")
