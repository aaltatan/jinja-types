"""Phase 3: the `str` namespace."""

import pytest
from jinja2 import Environment
from jinja2.exceptions import SecurityError
from jinja2.sandbox import ImmutableSandboxedEnvironment
from markupsafe import Markup

from jinja_types import JinjaTypesError, Registry, install
from jinja_types.types import str_


def test_every_public_str_member_is_registered() -> None:
    public = {name for name in dir(str) if not name.startswith("_")} - {"maketrans"}
    specs = Registry.default().specs()
    registered = {spec.member for spec in specs if spec.namespace.name == "str"}

    assert registered == public


def test_output_is_plain_str_and_escaped_once() -> None:
    env = ImmutableSandboxedEnvironment(autoescape=True)

    install(env)

    assert type(str_.upper("a")) is str
    assert env.from_string("{{ x | str.upper }}").render(x="<b>") == "&lt;B&gt;"
    assert env.from_string("{{ x | str.upper }}").render(x=Markup("<b>")) == "<B>"
    assert env.from_string("{{ x | str.replace('a', y) }}").render(x=Markup("a"), y="<i>") == (
        "&lt;i&gt;"
    )


@pytest.mark.parametrize("env", [Environment(), ImmutableSandboxedEnvironment()])
def test_format_is_always_sandboxed(env: Environment) -> None:
    install(env)

    assert env.from_string("{{ '[{0.__class__}]' | str.format(1) }}").render() == "[]"
    assert env.from_string("{{ '[{a.__class__}]' | str.format_map({'a': 1}) }}").render() == "[]"

    with pytest.raises(SecurityError, match="__class__"):
        env.from_string("{{ '{0.__class__.__mro__}' | str.format(1) }}").render()


def test_tests_and_errors() -> None:
    env = ImmutableSandboxedEnvironment()

    install(env)

    assert env.from_string("{{ 'x1' is str.isdigit }}").render() == "False"

    with pytest.raises(JinjaTypesError, match=r"str.index: ValueError: substring not found"):
        env.from_string("{{ 'abc' | str.index('z') }}").render()

    with pytest.raises(JinjaTypesError, match=r"str.upper: got 'int', expected str.*to_str"):
        env.from_string("{{ 5 | str.upper }}").render()

    with pytest.raises(JinjaTypesError, match="got an empty string"):
        env.from_string("{{ '' | str.join(['a']) }}").render()
