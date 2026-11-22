"""The catalog: a serializable view of every spec, for docs and autocomplete."""

import dataclasses
import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Self

from .spec import Example, Kind, MemberSpec, Param


@dataclass(frozen=True, slots=True)
class CatalogEntry:
    """One member as tooling sees it (no callables)."""

    name: str
    kinds: tuple[str, ...]
    namespace: str | None
    input_type: str | None
    params: tuple[Param, ...]
    returns: str
    doc: str
    examples: tuple[Example, ...]
    source: str
    replaced: bool
    constant: bool

    @classmethod
    def from_spec(cls, spec: MemberSpec) -> Self:
        return cls(
            name=spec.name,
            kinds=tuple(str(kind.name).lower() for kind in Kind if kind in spec.kinds),
            namespace=spec.namespace.name,
            input_type=spec.input_type,
            params=spec.params,
            returns=spec.returns,
            doc=spec.doc,
            examples=spec.examples,
            source=spec.source,
            replaced=spec.replaced,
            constant=spec.constant,
        )


@dataclass(frozen=True, slots=True)
class Catalog:
    """All catalog entries, sorted by name."""

    entries: tuple[CatalogEntry, ...]

    @classmethod
    def from_specs(cls, specs: Iterable[MemberSpec]) -> Self:
        return cls(tuple(CatalogEntry.from_spec(spec) for spec in specs))

    def __iter__(self) -> Iterator[CatalogEntry]:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def to_dict(self) -> dict[str, object]:
        return {"entries": [dataclasses.asdict(entry) for entry in self.entries]}

    def to_json(self, *, indent: int | None = 2) -> str:
        """Export as JSON. Non-JSON example context values are written as `repr()`."""
        return json.dumps(self.to_dict(), indent=indent, default=repr, ensure_ascii=False)
