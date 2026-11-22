"""Plugin discovery through the `jinja_types.plugins` entry-point group."""

from collections.abc import Iterable
from importlib.metadata import entry_points
from typing import TYPE_CHECKING

from .collection import Collection
from .errors import RegistryError

if TYPE_CHECKING:
    from .registry import Registry

PLUGIN_GROUP = "jinja_types.plugins"


def load_plugins(registry: "Registry", group: str = PLUGIN_GROUP) -> list[str]:
    """Include every plugin's collections, in entry-point name order. Return the plugin names.

    An entry point must load a `Collection` or an iterable of them.
    """

    loaded = []

    for ep in sorted(entry_points(group=group), key=lambda ep: ep.name):
        obj = ep.load()
        collections = [obj] if isinstance(obj, Collection) else _as_collections(ep.name, obj)

        registry.include(*collections, source=ep.name)
        loaded.append(ep.name)

    return loaded


def _as_collections(name: str, obj: object) -> list[Collection]:
    items: list[object] = list(obj) if isinstance(obj, Iterable) else [obj]
    collections = [item for item in items if isinstance(item, Collection)]

    if len(collections) != len(items):
        bad = next(item for item in items if not isinstance(item, Collection))

        raise RegistryError(
            f"plugin {name!r} must provide a Collection or an iterable of Collections, "
            f"got {type(bad).__name__}"
        )

    return collections
