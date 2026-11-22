"""Every type-member wrapper gives the same output as the real Python member.

Each example is rendered twice: once with the wrappers, once with filters that call the real
member directly (on a copy; a mutating member returns the mutated copy, as the wrappers do).
"""

import copy
from collections.abc import Callable
from zoneinfo import ZoneInfo

import pytest
from demo import demo_registry
from jinja2.filters import make_attrgetter
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import Kind, install
from jinja_types.core import Example, MemberSpec
from jinja_types.types.str_ import SANDBOX

REGISTRY = demo_registry()
MUTATING = {"append", "extend", "insert", "remove", "reverse", "sort", "clear", "update"}
# `re.*` wraps module functions, not type members
TYPE_SPECS = [spec for spec in REGISTRY.specs() if spec.namespace.name not in (None, "re")]
CASES = [
    pytest.param(example, id=f"{spec.name}-{i}")
    for spec in TYPE_SPECS
    for i, example in enumerate(spec.examples)
]


def real(spec: MemberSpec) -> Callable[..., object]:
    def call(value: object, /, *args: object, **kwargs: object) -> object:
        if spec.kinds & Kind.ATTRIBUTE:
            return getattr(value, spec.member)

        if spec.name == "datetime.astimezone":  # the one extension: IANA zone names
            args = tuple(ZoneInfo(arg) if isinstance(arg, str) else arg for arg in args)

        if spec.name == "list.sort" and isinstance(kwargs.get("key"), str):  # attribute names
            kwargs = {**kwargs, "key": make_attrgetter(SANDBOX, str(kwargs["key"]))}

        if spec.classmethod:
            return getattr(spec.namespace.type, spec.member)(value, *args, **kwargs)

        target = copy.copy(value)
        result = getattr(target, spec.member)(*args, **kwargs)

        return target if spec.member in MUTATING else result

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
