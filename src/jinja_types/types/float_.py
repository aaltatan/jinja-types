"""The `float` namespace."""

from jinja_types.core import Collection
from jinja_types.helpers import PARSERS

collection = Collection("float", float, parse=PARSERS["float"])


@collection.filter(
    examples=[
        ("{{ 2.0 | float.is_integer }}", {}, "True"),
        ("{{ 2.5 is float.is_integer }}", {}, "False"),
    ]
)
def is_integer(value: float, /) -> bool:
    """Return True if the float has no fractional part."""
    return value.is_integer()


@collection.filter(examples=[("{{ 0.75 | float.as_integer_ratio | join('/') }}", {}, "3/4")])
def as_integer_ratio(value: float, /) -> tuple[int, int]:
    """Return the exact ratio `(numerator, denominator)`."""
    return value.as_integer_ratio()


@collection.filter(member="hex", examples=[("{{ 3.0 | float.hex }}", {}, "0x1.8000000000000p+1")])
def hex_(value: float, /) -> str:
    """Return the hexadecimal representation."""
    return value.hex()


@collection.classmethod(examples=[("{{ '0x1.8p1' | float.fromhex }}", {}, "3.0")])
def fromhex(value: str, /) -> float:
    """Parse a hexadecimal float string (classmethod; the string is piped in)."""
    return float.fromhex(value)


@collection.filter(examples=[("{{ 2.5 | float.conjugate }}", {}, "2.5")])
def conjugate(value: float, /) -> float:
    """Return the complex conjugate (the value itself)."""
    return value.conjugate()


@collection.attribute(examples=[("{{ 2.5 | float.real }}", {}, "2.5")])
def real(value: float, /) -> float:
    """The real part (the value itself)."""
    return value.real


@collection.attribute(examples=[("{{ 2.5 | float.imag }}", {}, "0.0")])
def imag(value: float, /) -> float:
    """The imaginary part (always 0.0)."""
    return value.imag
