"""Every type-member wrapper gives the same output as the real Python member.

Each example is rendered twice: once with the wrappers, once with filters that call the real
member directly (on a copy, returning the copy when the member returns None, as for mutating
methods).
"""

import copy
from collections.abc import Callable

import pytest
from demo import demo_registry
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import Kind, install
from jinja_types.core import Example, MemberSpec

REGISTRY = demo_registry()
TYPE_SPECS = [spec for spec in REGISTRY.specs() if spec.namespace.name is not None]
CASES = [
    pytest.param(example, id=f"{spec.name}-{i}")
    for spec in TYPE_SPECS
    for i, example in enumerate(spec.examples)
]


def real(spec: MemberSpec) -> Callable[..., object]:
    def call(value: object, /, *args: object, **kwargs: object) -> object:
        if spec.kinds & Kind.ATTRIBUTE:
            return getattr(value, spec.member)

        if spec.classmethod:
            return getattr(spec.namespace.type, spec.member)(value, *args, **kwargs)

        target = copy.copy(value)
        result = getattr(target, spec.member)(*args, **kwargs)

        return target if result is None else result

    return call


def render(template: str, context: dict[str, object], *, use_real: bool) -> str:
    env = ImmutableSandboxedEnvironment()

    install(env, REGISTRY)

    if use_real:
        for spec in TYPE_SPECS:
            member = real(spec)

            if spec.kinds & (Kind.FILTER | Kind.ATTRIBUTE):
                env.filters[spec.name] = member

            if spec.kinds & Kind.TEST:
                env.tests[spec.name] = lambda *a, _m=member, **k: bool(_m(*a, **k))

    return env.from_string(template).render(**copy.deepcopy(context))


@pytest.mark.parametrize("example", CASES)
def test_parity(example: Example) -> None:
    template, context, _ = example

    assert render(template, dict(context), use_real=False) == render(
        template, dict(context), use_real=True
    )
