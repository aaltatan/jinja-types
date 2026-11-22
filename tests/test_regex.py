"""Phase 6: the `re` and `match` namespaces and the regex engine."""

import re

import pytest
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import JinjaTypesError, Kind, Registry, install
from jinja_types.core import CURRENT, Options
from jinja_types.regex import engine

REGISTRY = Registry.default()
BOLD = "{% macro bold(m) %}<b>{{ m | match.group(0) }}</b>{% endmacro %}"


def render(template: str, *, autoescape: bool = False, timeout: float = 1.0, **ctx: object) -> str:
    env = ImmutableSandboxedEnvironment(autoescape=autoescape)

    install(env, REGISTRY, regex_timeout=timeout)

    return env.from_string(template).render(**ctx)


def registered(namespace: str) -> set[str]:
    return {spec.member for spec in REGISTRY.specs() if spec.namespace.name == namespace}


def test_every_member_is_registered() -> None:
    functions = {"search", "match", "fullmatch", "findall", "finditer", "sub", "subn", "split"}

    assert registered("re") == functions | {"escape"}
    assert registered("match") == {n for n in dir(re.Match) if not n.startswith("_")} - {"regs"}


def test_search_match_fullmatch_are_tests() -> None:
    for name in ("re.search", "re.match", "re.fullmatch"):
        assert REGISTRY.get(name).kinds == Kind.FILTER | Kind.TEST


def test_phase_examples() -> None:
    template = r"""{{ "ABC-42" | re.search("abc-(\\d+)", flags=re.I) | match.group(1) }}"""

    assert render(template) == "42"
    assert render(r"""{% if "2026" is re.fullmatch("\\d{4}") %}yes{% endif %}""") == "yes"


@pytest.mark.parametrize(
    ("autoescape", "expected"),
    [(True, "&lt;<b>a</b>&gt; &amp; <b>a</b>"), (False, "<<b>a</b>> & <b>a</b>")],
)
def test_macro_replacement_escapes_once(autoescape: bool, expected: str) -> None:
    template = BOLD + "{{ x | re.sub('a', bold) }}"

    assert render(template, autoescape=autoescape, x="<a> & a") == expected


def test_macro_replacement_counts_and_empty_matches() -> None:
    upper = "{% macro up(m) %}-{% endmacro %}"

    assert render(upper + "{{ 'abxd' | re.sub('x*', up) }}") == re.sub("x*", "-", "abxd")
    assert render(upper + "{{ 'aaa' | re.subn('a', up, 2) | join('|') }}") == "--a|2"


def test_catastrophic_pattern_times_out() -> None:
    assert engine.regex is not None

    with pytest.raises(JinjaTypesError, match=r"TimeoutError.*larger regex_timeout"):
        render("{{ x | re.search('(a|aa)+$') }}", timeout=0.1, x="a" * 60 + "b")


def test_pattern_errors_carry_the_position() -> None:
    with pytest.raises(JinjaTypesError, match=r"re\.search: error: .* at position \d"):
        render("{{ 'x' | re.search('(') }}")


def test_value_must_be_a_string() -> None:
    with pytest.raises(JinjaTypesError, match=r"got 'int', expected str\. Hint: pass a str"):
        render("{{ 5 | re.search('5') }}")

    with pytest.raises(JinjaTypesError, match=r"got 'str', expected Match"):
        render("{{ 'x' | match.group }}")


def test_stdlib_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(engine, "regex", None)

    assert render("{{ x | re.search('b+') | match.span | join('-') }}", x="abbc") == "1-3"
    assert type(engine.call("search", "b", "abc")) is re.Match


def test_options_are_set_only_while_a_member_runs() -> None:
    seen: list[float] = []

    def spy(found: re.Match[str]) -> str:
        seen.append(CURRENT.get().regex_timeout)

        return ""

    render("{{ x | re.sub('a', spy) }}", timeout=0.5, x="a", spy=spy)

    assert seen == [0.5]
    assert CURRENT.get() == Options()
