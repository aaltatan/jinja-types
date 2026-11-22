"""Built-in collections, one module per namespace."""

from importlib.util import find_spec

from jinja_types.core.collection import Collection


def builtin_collections() -> list[Collection]:
    """Return every built-in collection, in registration order."""
    # local: these modules import core, which imports this module lazily
    from jinja_types import helpers
    from jinja_types.regex import match_, pattern_, re_

    from . import (
        ar_,
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

    numbers = [int_, bool_, float_, decimal_, fraction_]
    dates = [date_, datetime_, time_, timedelta_]
    modules = [str_, *numbers, *dates, list_, dict_, uuid_, path_, re_, pattern_, match_, ar_]

    if find_spec("babel") is not None:  # the [babel] extra
        from jinja_types.contrib import babel

        modules.append(babel)

    return [*helpers.collections, *(module.collection for module in modules)]
