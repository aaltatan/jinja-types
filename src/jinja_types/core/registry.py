"""The registry: combines collections, enforces conflict rules and dispatches by MRO."""

import dataclasses
from dataclasses import dataclass
from typing import Literal, Self

from .catalog import Catalog
from .collection import Collection
from .errors import DuplicateMemberError, RegistryError
from .namespace import Namespace
from .plugins import PLUGIN_GROUP, load_plugins
from .spec import MemberSpec


@dataclass(frozen=True, slots=True)
class Conflict:
    """One conflict-resolution decision, for docs and tooling."""

    name: str
    resolution: Literal["replaced", "dispatch"]
    detail: str


class Registry:
    """All known members, keyed by qualified name."""

    def __init__(self) -> None:
        self._specs: dict[str, MemberSpec] = {}
        self._namespaces: dict[str, Namespace] = {}
        self._by_type: dict[type, list[Namespace]] = {}
        self._replacements: list[Conflict] = []

    @classmethod
    def default(cls, *, plugins: bool = False) -> Self:
        """Return a registry with every built-in collection (and plugins, if asked)."""

        from jinja_types.types import builtin_collections  # local: types/ imports core

        registry = cls().include(*builtin_collections())

        if plugins:
            registry.load_plugins()

        return registry

    def include(
        self, *collections: Collection, replace: bool = False, source: str | None = None
    ) -> Self:
        """Add collections. Nothing changes if any of them conflicts."""

        specs = dict(self._specs)
        namespaces = dict(self._namespaces)
        replacements = list(self._replacements)

        for collection in collections:
            namespace = collection.namespace

            if namespace.name is not None:
                existing = namespaces.get(namespace.name)

                if existing is not None and existing.type is not namespace.type:
                    raise RegistryError(
                        f"namespace {namespace.name!r} is bound to {existing.type.__name__}, "
                        f"not {namespace.type.__name__}"
                    )

                if existing is None or existing.parse is None:
                    namespaces[namespace.name] = namespace

            for spec in collection:
                if source is not None:
                    spec = dataclasses.replace(spec, source=source)

                old = specs.get(spec.name)

                if old is not None:
                    if not replace:
                        raise DuplicateMemberError(
                            f"{spec.name} is already registered by {old.source!r}; "
                            "pass replace=True to override it"
                        )

                    spec = dataclasses.replace(spec, replaced=True)
                    replacements.append(
                        Conflict(spec.name, "replaced", f"{old.source} replaced by {spec.source}")
                    )

                specs[spec.name] = spec

        self._specs = specs
        self._namespaces = namespaces
        self._replacements = replacements
        self._by_type = {}

        for namespace in namespaces.values():
            self._by_type.setdefault(namespace.type, []).append(namespace)

        return self

    def load_plugins(self, group: str = PLUGIN_GROUP) -> Self:
        """Include every collection exposed through the `group` entry points."""

        load_plugins(self, group)

        return self

    def get(self, name: str) -> MemberSpec:
        """Return the spec registered under `name`, or raise `KeyError`."""

        return self._specs[name]

    def __contains__(self, name: object) -> bool:
        return name in self._specs

    def specs(self) -> list[MemberSpec]:
        """Return all specs, sorted by name."""

        return sorted(self._specs.values(), key=lambda spec: spec.name)

    def namespaces(self) -> list[Namespace]:
        """Return the named namespaces, sorted by name."""

        return sorted(self._namespaces.values(), key=lambda ns: ns.name or "")

    def namespace(self, name: str) -> Namespace:
        """Return the namespace registered as `name`, or raise `KeyError`."""

        return self._namespaces[name]

    def conflicts(self) -> list[Conflict]:
        """Return every replacement plus every parent/child member that MRO dispatch resolves."""

        dispatch = [
            Conflict(
                spec.name,
                "dispatch",
                f"overrides {parent.qualify(spec.member)} "
                f"for {spec.namespace.type.__name__} values",
            )
            for spec in self.specs()
            if spec.namespace.name is not None
            for parent in self.namespaces()
            if parent.type is not spec.namespace.type
            and issubclass(spec.namespace.type, parent.type)
            and parent.qualify(spec.member) in self._specs
        ]

        return [*self._replacements, *dispatch]

    def resolve(self, spec: MemberSpec, value: object) -> MemberSpec:
        """Return the most specific spec for `value`, walking its MRO up to the spec's type."""

        for cls in type(value).__mro__:
            if cls is spec.namespace.type:
                break

            for namespace in self._by_type.get(cls, ()):
                found = self._specs.get(namespace.qualify(spec.member))

                if found is not None:
                    return found

        return spec

    def supported(self, namespace: Namespace) -> tuple[str, ...]:
        """Return the type names a namespace accepts: its type plus registered subclasses."""

        names = [namespace.type.__name__]

        for other in self._namespaces.values():
            name = other.type.__name__

            if issubclass(other.type, namespace.type) and name not in names:
                names.append(name)

        return tuple(names)

    def catalog(self) -> Catalog:
        """Return the typed catalog of every spec."""

        return Catalog.from_specs(self.specs())

    def copy(self) -> Self:
        """Return an independent copy."""

        new = type(self)()
        new._specs = dict(self._specs)
        new._namespaces = dict(self._namespaces)
        new._by_type = {cls: list(nss) for cls, nss in self._by_type.items()}
        new._replacements = list(self._replacements)

        return new
