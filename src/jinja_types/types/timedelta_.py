"""The `timedelta` namespace. Not exposed: the constants `min`, `max`, `resolution`."""

from datetime import timedelta

from jinja_types.core import Collection
from jinja_types.helpers import PARSERS

collection = Collection("timedelta", timedelta, parse=PARSERS["timedelta"])

TD = timedelta(days=1, hours=1, seconds=1, microseconds=500)


@collection.filter(examples=[("{{ x | timedelta.total_seconds }}", {"x": TD}, "90001.0005")])
def total_seconds(value: timedelta, /) -> float:
    """Return the whole duration in seconds."""
    return value.total_seconds()


@collection.attribute(examples=[("{{ x | timedelta.days }}", {"x": TD}, "1")])
def days(value: timedelta, /) -> int:
    """The days part."""
    return value.days


@collection.attribute(examples=[("{{ x | timedelta.seconds }}", {"x": TD}, "3601")])
def seconds(value: timedelta, /) -> int:
    """The seconds part, below one day."""
    return value.seconds


@collection.attribute(examples=[("{{ x | timedelta.microseconds }}", {"x": TD}, "500")])
def microseconds(value: timedelta, /) -> int:
    """The microseconds part, below one second."""
    return value.microseconds
