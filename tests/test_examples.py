"""Run every spec's examples in a sandboxed environment, with autoescape on and off."""

import copy

import pytest
from demo import demo_registry
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import install
from jinja_types.core import Example

REGISTRY = demo_registry()
CASES = [
    pytest.param(example, id=f"{spec.name}-{i}")
    for spec in REGISTRY.specs()
    for i, example in enumerate(spec.examples)
]


def fresh(value: object) -> object:
    """A deep copy, so examples cannot leak changes; immutable uncopyable values are shared."""

    try:
        return copy.deepcopy(value)
    except TypeError:  # e.g. arapy nouns hold a mappingproxy
        return value


@pytest.mark.parametrize("autoescape", [False, True])
@pytest.mark.parametrize("example", CASES)
def test_example(example: Example, autoescape: bool) -> None:
    template, context, expected = example
    env = ImmutableSandboxedEnvironment(autoescape=autoescape)

    install(env, REGISTRY)

    assert (
        env.from_string(template).render({key: fresh(value) for key, value in context.items()})
        == expected
    )
