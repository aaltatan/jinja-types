"""The `decimal` namespace (`decimal.Decimal`): all 55 public members.

`rounding` arguments take the `decimal.ROUND_*` globals, and `context` arguments take a
`decimal.Context(...)` built in the template.
"""

from decimal import Context, Decimal, DecimalTuple

from jinja_types.core import Collection
from jinja_types.helpers import PARSERS

collection = Collection("decimal", Decimal, parse=PARSERS["decimal"])

type Other = Decimal | int

D = Decimal


def ex(template: str, expected: str, **context: object) -> tuple[str, dict[str, object], str]:
    """Shorthand for an example tuple."""
    return (template, context, expected)


# --- rounding and normalizing ----------------------------------------------------------------


@collection.filter(
    examples=[
        ex("{{ x | decimal.quantize(decimal.Decimal('0.01')) }}", "1.00", x=D("1.005")),
        ex(
            "{{ x | decimal.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)"
            " | fmt(',.2f') }}",
            "1,500.01",
            x=D("1500.005"),
        ),
    ]
)
def quantize(
    value: Decimal, /, exp: Other, rounding: str | None = None, context: Context | None = None
) -> Decimal:
    """Round to the exponent of `exp` (`decimal.Decimal('0.01')` gives two places)."""
    return value.quantize(exp, rounding, context)


@collection.filter(examples=[ex("{{ x | decimal.normalize }}", "1.2E+2", x=D("120.00"))])
def normalize(value: Decimal, /, context: Context | None = None) -> Decimal:
    """Strip trailing zeros (and use exponent form where needed)."""
    return value.normalize(context)


@collection.filter(
    examples=[
        ex("{{ x | decimal.to_integral }}", "2", x=D("2.5")),
        ex("{{ x | decimal.to_integral(decimal.ROUND_HALF_UP) }}", "3", x=D("2.5")),
    ]
)
def to_integral(
    value: Decimal, /, rounding: str | None = None, context: Context | None = None
) -> Decimal:
    """Round to an integer (same as `to_integral_value`)."""
    return value.to_integral(rounding, context)


@collection.filter(examples=[ex("{{ x | decimal.to_integral_exact }}", "4", x=D("3.7"))])
def to_integral_exact(
    value: Decimal, /, rounding: str | None = None, context: Context | None = None
) -> Decimal:
    """Round to an integer, signalling Inexact and Rounded when it changes."""
    return value.to_integral_exact(rounding, context)


@collection.filter(
    examples=[
        ex("{{ x | decimal.to_integral_value(rounding=decimal.ROUND_FLOOR) }}", "-4", x=D("-3.2"))
    ]
)
def to_integral_value(
    value: Decimal, /, rounding: str | None = None, context: Context | None = None
) -> Decimal:
    """Round to an integer without signalling Inexact or Rounded."""
    return value.to_integral_value(rounding, context)


@collection.filter(examples=[ex("{{ x | decimal.canonical }}", "1.50", x=D("1.50"))])
def canonical(value: Decimal, /) -> Decimal:
    """Return the canonical encoding (the value itself)."""
    return value.canonical()


# --- comparison --------------------------------------------------------------------------------


@collection.filter(
    examples=[
        ex("{{ x | decimal.compare(2) }}", "-1", x=D("1.5")),
        ex("{{ x | decimal.compare(y) }}", "0", x=D("1.50"), y=D("1.5")),
    ]
)
def compare(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Compare numerically: -1, 0 or 1 (NaN if either is NaN)."""
    return value.compare(other, context)


@collection.filter(examples=[ex("{{ x | decimal.compare_signal(1) }}", "1", x=D("2"))])
def compare_signal(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Like `compare`, but signal on any NaN."""
    return value.compare_signal(other, context)


@collection.filter(
    examples=[ex("{{ x | decimal.compare_total(y) }}", "-1", x=D("1.50"), y=D("1.5"))]
)
def compare_total(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Compare by abstract representation (1.50 sorts before 1.5)."""
    return value.compare_total(other, context)


@collection.filter(examples=[ex("{{ x | decimal.compare_total_mag(1) }}", "0", x=D("-1"))])
def compare_total_mag(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Like `compare_total`, ignoring signs."""
    return value.compare_total_mag(other, context)


@collection.filter(member="max", examples=[ex("{{ x | decimal.max(3) }}", "3", x=D("2.5"))])
def max_(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Return the larger of the value and `other`."""
    return value.max(other, context)


@collection.filter(member="min", examples=[ex("{{ x | decimal.min(3) }}", "2.5", x=D("2.5"))])
def min_(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Return the smaller of the value and `other`."""
    return value.min(other, context)


@collection.filter(examples=[ex("{{ x | decimal.max_mag(2) }}", "-3", x=D("-3"))])
def max_mag(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Return the one with the larger absolute value."""
    return value.max_mag(other, context)


@collection.filter(examples=[ex("{{ x | decimal.min_mag(2) }}", "2", x=D("-3"))])
def min_mag(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Return the one with the smaller absolute value."""
    return value.min_mag(other, context)


@collection.filter(
    examples=[
        ex("{{ x | decimal.same_quantum(y) }}", "True", x=D("1.10"), y=D("2.25")),
        ex("{{ x is decimal.same_quantum(1) }}", "False", x=D("1.1")),
    ]
)
def same_quantum(value: Decimal, /, other: Other, context: Context | None = None) -> bool:
    """Return True if both have the same exponent."""
    return value.same_quantum(other, context)


# --- math --------------------------------------------------------------------------------------


@collection.filter(examples=[ex("{{ x | decimal.sqrt }}", "1.414213562373095048801688724", x=D(2))])
def sqrt(value: Decimal, /, context: Context | None = None) -> Decimal:
    """Return the square root, to the context precision."""
    return value.sqrt(context)


@collection.filter(
    examples=[
        ex("{{ x | decimal.exp }}", "2.718281828459045235360287471", x=D(1)),
        ex("{{ x | decimal.exp(decimal.Context(prec=5)) }}", "2.7183", x=D(1)),
    ]
)
def exp(value: Decimal, /, context: Context | None = None) -> Decimal:
    """Return e raised to the value."""
    return value.exp(context)


@collection.filter(
    examples=[ex("{{ x | decimal.ln(decimal.Context(prec=5)) }}", "2.3026", x=D(10))]
)
def ln(value: Decimal, /, context: Context | None = None) -> Decimal:
    """Return the natural logarithm."""
    return value.ln(context)


@collection.filter(examples=[ex("{{ x | decimal.log10 }}", "3", x=D(1000))])
def log10(value: Decimal, /, context: Context | None = None) -> Decimal:
    """Return the base-10 logarithm."""
    return value.log10(context)


@collection.filter(examples=[ex("{{ x | decimal.logb }}", "2", x=D("250"))])
def logb(value: Decimal, /, context: Context | None = None) -> Decimal:
    """Return the adjusted exponent as a Decimal."""
    return value.logb(context)


@collection.filter(examples=[ex("{{ x | decimal.fma(3, 1) }}", "7", x=D(2))])
def fma(value: Decimal, /, other: Other, third: Other, context: Context | None = None) -> Decimal:
    """Fused multiply-add: `value * other + third`, rounded once."""
    return value.fma(other, third, context)


@collection.filter(examples=[ex("{{ x | decimal.remainder_near(3) }}", "1", x=D(10))])
def remainder_near(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Return the remainder of dividing by `other`, choosing the quotient nearest to exact."""
    return value.remainder_near(other, context)


@collection.filter(examples=[ex("{{ x | decimal.scaleb(2) }}", "1.5E+2", x=D("1.5"))])
def scaleb(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Return the value with its exponent adjusted by `other`."""
    return value.scaleb(other, context)


@collection.filter(
    examples=[ex("{{ x | decimal.next_plus }}", "1.000000000000000000000000001", x=D(1))]
)
def next_plus(value: Decimal, /, context: Context | None = None) -> Decimal:
    """Return the smallest representable number larger than the value."""
    return value.next_plus(context)


@collection.filter(
    examples=[ex("{{ x | decimal.next_minus(decimal.Context(prec=3)) }}", "0.999", x=D(1))]
)
def next_minus(value: Decimal, /, context: Context | None = None) -> Decimal:
    """Return the largest representable number smaller than the value."""
    return value.next_minus(context)


@collection.filter(
    examples=[ex("{{ x | decimal.next_toward(0, decimal.Context(prec=3)) }}", "0.999", x=D(1))]
)
def next_toward(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Return the next representable number toward `other`."""
    return value.next_toward(other, context)


# --- sign and copies ---------------------------------------------------------------------------


@collection.filter(examples=[ex("{{ x | decimal.copy_abs }}", "2.5", x=D("-2.5"))])
def copy_abs(value: Decimal, /) -> Decimal:
    """Return the absolute value, without rounding."""
    return value.copy_abs()


@collection.filter(examples=[ex("{{ x | decimal.copy_negate }}", "-2.5", x=D("2.5"))])
def copy_negate(value: Decimal, /) -> Decimal:
    """Return the negated value, without rounding."""
    return value.copy_negate()


@collection.filter(examples=[ex("{{ x | decimal.copy_sign(-1) }}", "-2.5", x=D("2.5"))])
def copy_sign(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Return the value with the sign of `other`."""
    return value.copy_sign(other, context)


@collection.filter(examples=[ex("{{ x | decimal.conjugate }}", "2.5", x=D("2.5"))])
def conjugate(value: Decimal, /) -> Decimal:
    """Return the complex conjugate (the value itself)."""
    return value.conjugate()


# --- digit-wise logic and shifts (operands made of 0s and 1s) ----------------------------------


@collection.filter(examples=[ex("{{ x | decimal.logical_and(1010) }}", "1000", x=D(1100))])
def logical_and(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Digit-wise AND of two logical operands."""
    return value.logical_and(other, context)


@collection.filter(examples=[ex("{{ x | decimal.logical_or(1010) }}", "1110", x=D(1100))])
def logical_or(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Digit-wise OR of two logical operands."""
    return value.logical_or(other, context)


@collection.filter(examples=[ex("{{ x | decimal.logical_xor(1010) }}", "110", x=D(1100))])
def logical_xor(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Digit-wise XOR of two logical operands."""
    return value.logical_xor(other, context)


@collection.filter(
    examples=[ex("{{ x | decimal.logical_invert(decimal.Context(prec=4)) }}", "11", x=D(1100))]
)
def logical_invert(value: Decimal, /, context: Context | None = None) -> Decimal:
    """Digit-wise inversion of a logical operand, to the context precision."""
    return value.logical_invert(context)


@collection.filter(
    examples=[ex("{{ x | decimal.rotate(1, decimal.Context(prec=4)) }}", "2341", x=D(1234))]
)
def rotate(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Rotate the digits by `other` places, to the context precision."""
    return value.rotate(other, context)


@collection.filter(
    examples=[ex("{{ x | decimal.shift(1, decimal.Context(prec=4)) }}", "2340", x=D(1234))]
)
def shift(value: Decimal, /, other: Other, context: Context | None = None) -> Decimal:
    """Shift the digits by `other` places, to the context precision."""
    return value.shift(other, context)


# --- inspection --------------------------------------------------------------------------------


@collection.filter(examples=[ex("{{ x | decimal.adjusted }}", "2", x=D("123.45"))])
def adjusted(value: Decimal, /) -> int:
    """Return the exponent of the most significant digit."""
    return value.adjusted()


@collection.filter(
    examples=[ex("{{ x | decimal.as_integer_ratio | join('/') }}", "5/4", x=D("1.25"))]
)
def as_integer_ratio(value: Decimal, /) -> tuple[int, int]:
    """Return the exact ratio `(numerator, denominator)`."""
    return value.as_integer_ratio()


@collection.filter(
    examples=[
        ex(
            "{{ x | decimal.as_tuple }}",
            "DecimalTuple(sign=1, digits=(1, 5), exponent=-1)",
            x=D("-1.5"),
        )
    ]
)
def as_tuple(value: Decimal, /) -> DecimalTuple:
    """Return `(sign, digits, exponent)`."""
    return value.as_tuple()


@collection.filter(examples=[ex("{{ x | decimal.number_class }}", "-Normal", x=D("-1.5"))])
def number_class(value: Decimal, /, context: Context | None = None) -> str:
    """Return the class of the number, such as `+Normal` or `-Zero`."""
    return value.number_class(context)


@collection.filter(examples=[ex("{{ x | decimal.radix }}", "10", x=D(1))])
def radix(value: Decimal, /) -> Decimal:
    """Return 10, the radix of Decimal arithmetic."""
    return value.radix()


@collection.filter(examples=[ex("{{ x | decimal.to_eng_string }}", "123E+3", x=D("1.23E+5"))])
def to_eng_string(value: Decimal, /, context: Context | None = None) -> str:
    """Return engineering notation (exponent a multiple of 3)."""
    return value.to_eng_string(context)


@collection.attribute(examples=[ex("{{ x | decimal.real }}", "2.5", x=D("2.5"))])
def real(value: Decimal, /) -> Decimal:
    """The real part (the value itself)."""
    return value.real


@collection.attribute(examples=[ex("{{ x | decimal.imag }}", "0", x=D("2.5"))])
def imag(value: Decimal, /) -> Decimal:
    """The imaginary part (always 0)."""
    return value.imag


@collection.classmethod(examples=[ex("{{ 0.5 | decimal.from_float }}", "0.5")])
def from_float(value: float | int, /) -> Decimal:
    """Return the exact Decimal for a float (classmethod; the float is piped in)."""
    return Decimal.from_float(value)


# --- predicates (filters and tests) ------------------------------------------------------------


@collection.filter(examples=[ex("{{ x | decimal.is_canonical }}", "True", x=D(1))])
def is_canonical(value: Decimal, /) -> bool:
    """Return True (Decimals are always canonical)."""
    return value.is_canonical()


@collection.filter(
    examples=[
        ex("{{ x | decimal.is_finite }}", "True", x=D(1)),
        ex("{{ x is decimal.is_finite }}", "False", x=D("Inf")),
    ]
)
def is_finite(value: Decimal, /) -> bool:
    """Return True if the value is neither infinite nor NaN."""
    return value.is_finite()


@collection.filter(examples=[ex("{{ x | decimal.is_infinite }}", "True", x=D("-Inf"))])
def is_infinite(value: Decimal, /) -> bool:
    """Return True if the value is infinite."""
    return value.is_infinite()


@collection.filter(examples=[ex("{{ x | decimal.is_nan }}", "True", x=D("NaN"))])
def is_nan(value: Decimal, /) -> bool:
    """Return True if the value is a NaN (quiet or signalling)."""
    return value.is_nan()


@collection.filter(examples=[ex("{{ x | decimal.is_qnan }}", "True", x=D("NaN"))])
def is_qnan(value: Decimal, /) -> bool:
    """Return True if the value is a quiet NaN."""
    return value.is_qnan()


@collection.filter(examples=[ex("{{ x | decimal.is_snan }}", "True", x=D("sNaN"))])
def is_snan(value: Decimal, /) -> bool:
    """Return True if the value is a signalling NaN."""
    return value.is_snan()


@collection.filter(examples=[ex("{{ x | decimal.is_normal }}", "True", x=D("1.5"))])
def is_normal(value: Decimal, /, context: Context | None = None) -> bool:
    """Return True if the value is a normal finite non-zero number."""
    return value.is_normal(context)


@collection.filter(examples=[ex("{{ x | decimal.is_subnormal }}", "True", x=D("1E-999999999"))])
def is_subnormal(value: Decimal, /, context: Context | None = None) -> bool:
    """Return True if the value is subnormal."""
    return value.is_subnormal(context)


@collection.filter(
    examples=[
        ex("{{ x | decimal.is_signed }}", "True", x=D("-1")),
        ex("{{ x is decimal.is_signed }}", "True", x=D("-0")),
    ]
)
def is_signed(value: Decimal, /) -> bool:
    """Return True if the sign is negative (including -0)."""
    return value.is_signed()


@collection.filter(examples=[ex("{{ x | decimal.is_zero }}", "True", x=D("0.00"))])
def is_zero(value: Decimal, /) -> bool:
    """Return True if the value is zero (of either sign)."""
    return value.is_zero()
