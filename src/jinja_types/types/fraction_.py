"""The `fraction` namespace (`fractions.Fraction`)."""

from decimal import Decimal
from fractions import Fraction

from jinja_types.core import Collection
from jinja_types.helpers import PARSERS

collection = Collection("fraction", Fraction, parse=PARSERS["fraction"])

PI = Fraction("3.141592653589793")
THIRD = Fraction(1, 3)


@collection.filter(
    examples=[
        ("{{ x | fraction.limit_denominator(10) }}", {"x": PI}, "22/7"),
        ("{{ x | fraction.limit_denominator }}", {"x": PI}, "3126535/995207"),
    ]
)
def limit_denominator(value: Fraction, /, max_denominator: int = 1000000) -> Fraction:
    """Return the closest fraction with a denominator of at most `max_denominator`."""
    return value.limit_denominator(max_denominator)


@collection.filter(
    examples=[("{{ x | fraction.as_integer_ratio | join('/') }}", {"x": THIRD}, "1/3")]
)
def as_integer_ratio(value: Fraction, /) -> tuple[int, int]:
    """Return `(numerator, denominator)`."""
    return value.as_integer_ratio()


@collection.filter(
    examples=[
        ("{{ x | fraction.is_integer }}", {"x": Fraction(4, 2)}, "True"),
        ("{{ x is fraction.is_integer }}", {"x": THIRD}, "False"),
    ]
)
def is_integer(value: Fraction, /) -> bool:
    """Return True if the fraction is a whole number."""
    return value.is_integer()


@collection.filter(examples=[("{{ x | fraction.conjugate }}", {"x": THIRD}, "1/3")])
def conjugate(value: Fraction, /) -> Fraction:
    """Return the complex conjugate (the value itself)."""
    return value.conjugate()


@collection.attribute(examples=[("{{ x | fraction.numerator }}", {"x": Fraction(6, 4)}, "3")])
def numerator(value: Fraction, /) -> int:
    """The numerator, in lowest terms."""
    return value.numerator


@collection.attribute(examples=[("{{ x | fraction.denominator }}", {"x": Fraction(6, 4)}, "2")])
def denominator(value: Fraction, /) -> int:
    """The denominator, in lowest terms."""
    return value.denominator


@collection.attribute(examples=[("{{ x | fraction.real }}", {"x": THIRD}, "1/3")])
def real(value: Fraction, /) -> Fraction:
    """The real part (the value itself)."""
    return value.real


@collection.attribute(examples=[("{{ x | fraction.imag }}", {"x": THIRD}, "0")])
def imag(value: Fraction, /) -> int:
    """The imaginary part (always 0)."""
    return value.imag


@collection.classmethod(examples=[("{{ 0.5 | fraction.from_float }}", {}, "1/2")])
def from_float(value: float, /) -> Fraction:
    """Return the exact fraction for a float (classmethod; the float is piped in)."""
    return Fraction.from_float(value)


@collection.classmethod(
    examples=[("{{ x | fraction.from_decimal }}", {"x": Decimal("1.25")}, "5/4")]
)
def from_decimal(value: Decimal, /) -> Fraction:
    """Return the exact fraction for a Decimal (classmethod; the Decimal is piped in)."""
    return Fraction.from_decimal(value)
