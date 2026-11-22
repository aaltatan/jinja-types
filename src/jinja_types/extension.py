"""Installing a registry into a Jinja environment."""

import dataclasses
from typing import ClassVar, Unpack, cast

from jinja2 import Environment
from jinja2.ext import Extension

from .core import BuiltinClashError, Invoker, Kind, Options, OptionsKwargs, Registry
from .core.invoker import MARK


def install(
    env: Environment,
    registry: Registry | None = None,
    *,
    options: Options | None = None,
    **kwargs: Unpack[OptionsKwargs],
) -> Registry:
    """Register every filter, test and global of `registry` (default: `Registry.default()`).

    Raises `BuiltinClashError`, before changing anything, if a plain-name helper is already a
    filter, test or global in `env`. Returns the registry that was installed.
    """

    registry = registry or Registry.default()
    options = dataclasses.replace(options or Options(), **kwargs)
    tables = (
        (Kind.FILTER | Kind.ATTRIBUTE, "filter", env.filters),
        (Kind.TEST, "test", env.tests),
        (Kind.GLOBAL, "global", env.globals),
    )

    for spec in registry.specs():
        if spec.namespace.name is not None:
            continue  # dotted names cannot clash with Jinja built-ins

        for kinds, label, table in tables:
            existing = table.get(spec.name)
            ours = hasattr(existing, MARK) or (spec.constant and existing is spec.func())

            if spec.kinds & kinds and existing is not None and not ours:
                raise BuiltinClashError(
                    f"{spec.name!r} clashes with the existing Jinja {label} of the same name"
                )

    invoker = Invoker(registry, options)

    for spec in registry.specs():
        if spec.kinds & (Kind.FILTER | Kind.ATTRIBUTE):
            env.filters[spec.name] = invoker.filter(spec)

        if spec.kinds & Kind.TEST:
            env.tests[spec.name] = invoker.test(spec)

        if spec.kinds & Kind.GLOBAL:
            env.globals[spec.name] = spec.func() if spec.constant else invoker.global_(spec)

    return registry


class TypesExtension(Extension):
    """Jinja extension that installs jinja-types.

    Use `TypesExtension` for the defaults, or `TypesExtension.configure(registry=..., coerce=True)`.
    """

    registry: ClassVar[Registry | None] = None
    options: ClassVar[Options] = Options()

    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)

        install(environment, self.registry, options=self.options)

    @classmethod
    def configure(
        cls, registry: Registry | None = None, **options: Unpack[OptionsKwargs]
    ) -> type["TypesExtension"]:
        """Return a subclass bound to `registry` and `options` (Jinja passes only the env)."""

        attrs = {"registry": registry, "options": Options(**options)}

        return cast(type[TypesExtension], type(cls.__name__, (cls,), attrs))
