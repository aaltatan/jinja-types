"""Phase 7: the `list` and `dict` namespaces."""

import pytest
from jinja2.exceptions import SecurityError
from jinja2.sandbox import ImmutableSandboxedEnvironment
from test_no_mutation import CASES

from jinja_types import JinjaTypesError, Registry, install

REGISTRY = Registry.default()


def render(template: str, **context: object) -> str:
    env = ImmutableSandboxedEnvironment()

    install(env, REGISTRY)

    return env.from_string(template).render(**context)


@pytest.mark.parametrize(("namespace", "cls"), [("list", list), ("dict", dict)])
def test_every_member_is_registered_and_checked_for_mutation(namespace: str, cls: type) -> None:
    public = {name for name in dir(cls) if not name.startswith("_")}
    registered = {spec.member for spec in REGISTRY.specs() if spec.namespace.name == namespace}
    checked = {str(case.id).split("-")[0] for case in CASES}

    assert registered == public
    assert {f"{namespace}.{member}" for member in public} <= checked


def test_mutating_members_return_new_objects() -> None:
    xs = [3, 1, 2]
    prices = {"tea": 2}

    template = (
        "{{ xs | list.sort }}{{ xs | list.pop }}{{ xs | list.clear }}"
        "{{ prices | dict.update(milk=1) | length }}{{ prices | dict.popitem | length }}"
    )

    assert render(template, xs=xs, prices=prices) == "[1, 2, 3]2[]22"
    assert xs == [3, 1, 2]
    assert prices == {"tea": 2}


def test_sort_key_attribute_paths_and_the_sandbox() -> None:
    rows = [{"a": {"b": 2}}, {"a": {"b": 1}}]

    assert render("{{ rows | list.sort(key='a.b') | map(attribute='a.b') | join }}", rows=rows) == (
        "12"
    )

    # attribute keys go through the sandbox, so unsafe attributes are refused
    with pytest.raises(SecurityError, match="__class__"):
        render("{{ xs | list.sort(key='__class__') }}", xs=[1, 2])


def test_errors() -> None:
    with pytest.raises(JinjaTypesError, match=r"got 'tuple', expected list"):
        render("{{ (1, 2) | list.copy }}")

    with pytest.raises(JinjaTypesError, match=r"dict\.pop: KeyError: 'milk'"):
        render("{{ {'tea': 1} | dict.pop('milk') }}")

    with pytest.raises(JinjaTypesError, match=r"list\.remove: ValueError"):
        render("{{ [1] | list.remove(2) }}")
