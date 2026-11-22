"""Built-in collections, one module per namespace."""

from jinja_types.core.collection import Collection


def builtin_collections() -> list[Collection]:
    """Return every built-in collection, in registration order."""
    # local: these modules import core, which imports this module lazily
    from jinja_types import helpers
    from jinja_types.regex import match_, re_

    from . import (
        bool_,
        date_,
        datetime_,
        decimal_,
        dict_,
        float_,
        fraction_,
        int_,
        list_,
        path_,
        str_,
        time_,
        timedelta_,
        uuid_,
    )

    modules = [
        str_,
        int_,
        list_,
        path_,
        bool_,
        float_,
        decimal_,
        dict_,
        fraction_,
        date_,
        datetime_,
        time_,
        timedelta_,
        uuid_,
        re_,
        match_,
    ]

    return [*helpers.collections, *(module.collection for module in modules)]
