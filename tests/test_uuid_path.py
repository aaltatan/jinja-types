"""Phase 8: the `uuid` and `path` namespaces."""

import builtins
import io
import os
import sys
from pathlib import PurePath
from uuid import UUID

import pytest
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import JinjaTypesError, Registry, install

REGISTRY = Registry.default()

# The explicit allowlist: pure members only. Anything added to `path.*` must be added here.
PATH_ALLOWLIST = {
    "name", "stem", "suffix", "suffixes", "parent", "parents", "parts", "anchor", "drive",
    "root", "as_posix", "as_uri", "with_name", "with_stem", "with_suffix", "joinpath",
    "relative_to", "is_relative_to", "is_absolute", "match",
}  # fmt: skip

if sys.version_info >= (3, 13):
    PATH_ALLOWLIST.add("full_match")


def render(template: str, *, coerce: bool = False, **context: object) -> str:
    env = ImmutableSandboxedEnvironment()

    install(env, REGISTRY, coerce=coerce)

    return env.from_string(template).render(**context)


def registered(namespace: str) -> set[str]:
    return {spec.member for spec in REGISTRY.specs() if spec.namespace.name == namespace}


def test_every_uuid_attribute_is_registered() -> None:
    assert registered("uuid") == {n for n in dir(UUID) if not n.startswith("_")}


def test_path_members_are_the_pure_allowlist() -> None:
    pure = {n for n in dir(PurePath) if not n.startswith("_")}

    assert registered("path") == PATH_ALLOWLIST
    assert pure - {"is_reserved", "with_segments"} >= PATH_ALLOWLIST


def test_no_path_member_performs_io(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("path.* touched the disk")

    for module, name in [
        (builtins, "open"),
        (io, "open"),
        (os, "stat"),
        (os, "lstat"),
        (os, "listdir"),
        (os, "scandir"),
        (os, "getcwd"),
        (os.path, "exists"),
        (os.path, "realpath"),
        (os.path, "abspath"),
    ]:
        monkeypatch.setattr(module, name, forbidden)

    examples = [
        e for spec in REGISTRY.specs() if spec.namespace.name == "path" for e in spec.examples
    ]

    env = ImmutableSandboxedEnvironment()

    install(env, REGISTRY)

    for template, context, expected in examples:
        assert env.from_string(template).render(context) == expected


def test_strings_need_conversion_or_coerce() -> None:
    with pytest.raises(JinjaTypesError, match=r"got 'str', expected PurePath\. Hint: .*to_path"):
        render("{{ 'a/b.txt' | path.suffix }}")

    assert render("{{ 'a/b.txt' | path.suffix }}", coerce=True) == ".txt"
    assert render("{{ 'a/b.txt' | to_path | path.stem }}") == "b"
    assert (
        render("{{ x | uuid.version }}", coerce=True, x="c232ab00-9414-11ec-b3c8-9f6bdeced846")
        == "1"
    )


def test_relative_to_errors_are_translated() -> None:
    with pytest.raises(JinjaTypesError, match=r"path\.relative_to: ValueError"):
        render("{{ 'a/b' | to_path | path.relative_to('c') }}")
