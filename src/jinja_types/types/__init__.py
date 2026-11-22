"""Built-in collections, one module per namespace."""

from jinja_types.core.collection import Collection


def builtin_collections() -> list[Collection]:
    """Return every built-in collection, in registration order."""
    # local: these modules import core, which imports this module lazily
    from jinja_types import helpers

    from . import str_

    return [*helpers.collections, str_.collection]
