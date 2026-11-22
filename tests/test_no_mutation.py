"""List and dict members never mutate their input."""

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
    if issubclass(spec.namespace.type, list | dict)
    for i, example in enumerate(spec.examples)
]


@pytest.mark.parametrize("example", CASES)
def test_input_is_not_mutated(example: Example) -> None:
    template, context, _ = example
    env = ImmutableSandboxedEnvironment()
    before = copy.deepcopy(dict(context))
    live = copy.deepcopy(before)

    install(env, REGISTRY)
    env.from_string(template).render(**live)

    assert live == before
