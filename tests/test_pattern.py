"""Phase 12: `re.compile` and the `pattern` namespace."""

import re

import pytest
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import JinjaTypesError, Kind, Registry, install
from jinja_types.regex import engine

REGISTRY = Registry.default()
BOLD = "{% macro bold(m) %}<b>{{ m | match.group(0) }}</b>{% endmacro %}"


def render(template: str, *, autoescape: bool = False, timeout: float = 1.0, **ctx: object) -> str:
    env = ImmutableSandboxedEnvironment(autoescape=autoescape)

    install(env, REGISTRY, regex_timeout=timeout)

    return env.from_string(template).render(**ctx)


@pytest.fixture(params=["regex", "re"])
def engine_name(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> str:
    if request.param == "re":
        monkeypatch.setattr(engine, "regex", None)

    return str(request.param)


def test_every_member_is_registered() -> None:
    members = {spec.member for spec in REGISTRY.specs() if spec.namespace.name == "pattern"}

    assert members == {n for n in dir(re.Pattern) if not n.startswith("_")} - {"scanner"}

    for name in ("pattern.search", "pattern.match", "pattern.fullmatch"):
        assert REGISTRY.get(name).kinds == Kind.FILTER | Kind.TEST


def test_phase_example(engine_name: str) -> None:
    template = r"""{% set word = re.compile("\\w+", re.I) %}{{ word | pattern.findall(text) }}"""
    compiled = render("{{ re.compile('a') }}")

    assert render(template, text="Hi, you") == "['Hi', 'you']"
    assert compiled.startswith("regex.Regex(" if engine_name == "regex" else "re.compile(")


def test_macro_replacement_escapes_once(engine_name: str) -> None:
    template = BOLD + "{{ re.compile('a') | pattern.sub(bold, x) }}"

    assert render(template, autoescape=True, x="<a> & a") == "&lt;<b>a</b>&gt; &amp; <b>a</b>"


def test_catastrophic_compiled_pattern_times_out() -> None:
    assert engine.regex is not None

    with pytest.raises(JinjaTypesError, match=r"pattern\.search: TimeoutError"):
        render("{{ re.compile('(a|aa)+$') | pattern.search(x) }}", timeout=0.1, x="a" * 60 + "b")


def test_compile_is_cached_per_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    assert engine.compile("x+", re.I) is engine.compile("x+", re.I)

    monkeypatch.setattr(engine, "regex", None)

    assert type(engine.compile("x+", re.I)) is re.Pattern


def test_stdlib_pattern_from_the_context_under_regex() -> None:
    assert engine.regex is not None
    assert render("{{ p | pattern.split('a1b') | join('|') }}", p=re.compile(r"\d")) == "a|b"


def test_errors() -> None:
    with pytest.raises(JinjaTypesError, match=r"re\.compile: error: .* at position \d"):
        render("{{ re.compile('(') }}")

    with pytest.raises(JinjaTypesError, match=r"got 'str', expected Pattern"):
        render("{{ 'x' | pattern.search('x') }}")
