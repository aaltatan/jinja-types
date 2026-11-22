"""Built-in collections, one module per namespace (added from Phase 3 on)."""

from jinja_types.core.collection import Collection


def builtin_collections() -> list[Collection]:
    """Return every built-in collection, in registration order."""
    from jinja_types import helpers  # local: helpers import core, which imports this lazily

    return [*helpers.collections]
