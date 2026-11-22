"""The `int` namespace. `bool` is a subclass of `int`, so every `int.*` member accepts bools."""

from collections.abc import Iterable
from typing import Literal

from jinja_types.core import Collection
from jinja_types.helpers import PARSERS

collection = Collection("int", int, parse=PARSERS["int"])


@collection.filter(examples=[("{{ 255 | int.bit_length }}", {}, "8")])
def bit_length(value: int, /) -> int:
    """Return the number of bits needed to represent the value, without sign."""
    return value.bit_length()


@collection.filter(examples=[("{{ 255 | int.bit_count }}", {}, "8")])
def bit_count(value: int, /) -> int:
    """Return the number of ones in the binary form of the absolute value."""
    return value.bit_count()


@collection.filter(
    examples=[
        ("{{ 1024 | int.to_bytes(2) | list }}", {}, "[4, 0]"),
        ("{{ 1024 | int.to_bytes(2, 'little') | list }}", {}, "[0, 4]"),
        ("{{ -1 | int.to_bytes(1, signed=True) | list }}", {}, "[255]"),
    ]
)
def to_bytes(
    value: int,
    /,
    length: int = 1,
    byteorder: Literal["little", "big"] = "big",
    *,
    signed: bool = False,
) -> bytes:
    """Return the bytes representing the value."""
    return value.to_bytes(length, byteorder, signed=signed)


@collection.classmethod(
    examples=[
        ("{{ [4, 0] | int.from_bytes }}", {}, "1024"),
        ("{{ [255] | int.from_bytes(signed=True) }}", {}, "-1"),
        ("{{ data | int.from_bytes('little') }}", {"data": b"\x00\x04"}, "1024"),
    ]
)
def from_bytes(
    value: bytes | Iterable[int],
    /,
    byteorder: Literal["little", "big"] = "big",
    *,
    signed: bool = False,
) -> int:
    """Return the integer represented by the bytes (classmethod; the bytes are piped in)."""
    return int.from_bytes(value, byteorder, signed=signed)


@collection.filter(examples=[("{{ 5 | int.as_integer_ratio | join('/') }}", {}, "5/1")])
def as_integer_ratio(value: int, /) -> tuple[int, int]:
    """Return `(value, 1)`."""
    return value.as_integer_ratio()


@collection.filter(examples=[("{{ 5 | int.is_integer }}", {}, "True")])
def is_integer(value: int, /) -> bool:
    """Return True (for duck-type compatibility with float)."""
    return value.is_integer()


@collection.filter(examples=[("{{ 5 | int.conjugate }}", {}, "5")])
def conjugate(value: int, /) -> int:
    """Return the complex conjugate (the value itself)."""
    return value.conjugate()


@collection.attribute(
    examples=[("{{ 5 | int.real }}", {}, "5"), ("{{ true | int.real }}", {}, "1")]
)
def real(value: int, /) -> int:
    """The real part (the value itself, as an int)."""
    return value.real


@collection.attribute(examples=[("{{ 5 | int.imag }}", {}, "0")])
def imag(value: int, /) -> int:
    """The imaginary part (always 0)."""
    return value.imag


@collection.attribute(examples=[("{{ 5 | int.numerator }}", {}, "5")])
def numerator(value: int, /) -> int:
    """The numerator (the value itself)."""
    return value.numerator


@collection.attribute(examples=[("{{ 5 | int.denominator }}", {}, "1")])
def denominator(value: int, /) -> int:
    """The denominator (always 1)."""
    return value.denominator
