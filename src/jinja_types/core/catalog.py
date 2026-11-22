"""The catalog: a serializable view of every spec, for docs and autocomplete."""

import builtins
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
    classmethod: bool

    @builtins.classmethod  # the `classmethod` field shadows the name here
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
            classmethod=spec.classmethod,
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

    def namespaces(self) -> list[str]:
        """Return the namespace labels in use, sorted (`helpers` for plain names)."""
        return sorted({label(entry) for entry in self.entries})

    def select(self, *, namespace: str | None = None, kind: str | None = None) -> Self:
        """Keep the entries in `namespace` (a label, see `namespaces`) and with `kind`."""

        return type(self)(
            tuple(
                entry
                for entry in self.entries
                if namespace in (None, label(entry)) and kind in (None, *entry.kinds)
            )
        )

    def to_markdown(self) -> str:
        """Export as Markdown: one `#` section per namespace, one `##` section per member."""

        lines: list[str] = []

        for namespace in self.namespaces():
            lines += [f"# `{namespace}`", ""]

            for entry in self.select(namespace=namespace):
                lines += entry_markdown(entry)

        return "\n".join(lines)


def label(entry: CatalogEntry) -> str:
    """The namespace label: the namespace name, or `helpers` for plain names."""
    return entry.namespace or "helpers"


def signature(entry: CatalogEntry) -> str:
    """Return a Python-style signature, e.g. `str.zfill(value: str, /, width: int) -> str`."""

    parts = [] if entry.input_type is None else [f"value: {entry.input_type}"]
    positional_only = entry.input_type is not None
    starred = False

    for param in entry.params:
        if positional_only and param.kind != "positional_only":
            parts.append("/")
            positional_only = False

        if param.kind == "keyword_only" and not starred:
            parts.append("*")

        prefix = {"var_positional": "*", "var_keyword": "**"}.get(param.kind, "")
        default = "" if param.default is None else f" = {param.default}"
        starred = starred or param.kind in ("var_positional", "keyword_only")

        parts.append(f"{prefix}{param.name}: {param.annotation}{default}")

    if positional_only:
        parts.append("/")

    return f"{entry.name}({', '.join(parts)}) -> {entry.returns}"


def entry_markdown(entry: CatalogEntry) -> list[str]:
    """Return the Markdown lines for one member."""

    tags = [*entry.kinds]

    if entry.classmethod:
        tags.append("classmethod")

    if entry.source != "jinja_types":
        tags.append(f"from {entry.source}" + (" (replaced)" if entry.replaced else ""))

    lines = [f"## `{entry.name}`", "", f"`{signature(entry)}`", "", f"*{', '.join(tags)}*", ""]

    if entry.doc:
        lines += [entry.doc, ""]

    for template, context, output in entry.examples:
        given = ", ".join(f"`{key} = {value!r}`" for key, value in context.items())
        suffix = f" with {given}" if given else ""

        lines.append(f"- ``{template}``{suffix} → ``{output}``")

    return [*lines, ""]
