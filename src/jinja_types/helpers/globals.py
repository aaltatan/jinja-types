"""Template globals: the `decimal`, `re`, `random` and `secrets` namespace objects, `today()`,
`now()`, `uuid1()`, `uuid4()` and `uuid5()`.

Globals and filters are separate Jinja tables, so the global `decimal` and the filter
`decimal.quantize` coexist.
"""

import decimal as _decimal
import random as _random
import re as _re
import secrets as _secrets
from collections.abc import Callable, Iterable, Sequence
from datetime import UTC, date, datetime, tzinfo
from typing import ClassVar
from uuid import NAMESPACE_DNS, UUID
from uuid import uuid1 as _uuid1
from uuid import uuid4 as _uuid4
from uuid import uuid5 as _uuid5

from jinja_types.core import Collection, JinjaTypesError
from jinja_types.regex import engine

collection = Collection()


class DecimalNamespace:
    """The `decimal` global: `Decimal`, `Context` and every `ROUND_*` constant."""

    Decimal: ClassVar = _decimal.Decimal
    Context: ClassVar = _decimal.Context
    ROUND_UP: ClassVar = _decimal.ROUND_UP
    ROUND_DOWN: ClassVar = _decimal.ROUND_DOWN
    ROUND_CEILING: ClassVar = _decimal.ROUND_CEILING
    ROUND_FLOOR: ClassVar = _decimal.ROUND_FLOOR
    ROUND_HALF_UP: ClassVar = _decimal.ROUND_HALF_UP
    ROUND_HALF_DOWN: ClassVar = _decimal.ROUND_HALF_DOWN
    ROUND_HALF_EVEN: ClassVar = _decimal.ROUND_HALF_EVEN
    ROUND_05UP: ClassVar = _decimal.ROUND_05UP

    def __repr__(self) -> str:
        return "<jinja_types decimal>"


class ReFlags:
    """The `re` global: regex flags (short and long names) and `compile`."""

    NOFLAG: ClassVar = _re.NOFLAG
    A: ClassVar = _re.A
    ASCII: ClassVar = _re.ASCII
    I: ClassVar = _re.I  # noqa: E741 (the stdlib name)
    IGNORECASE: ClassVar = _re.IGNORECASE
    L: ClassVar = _re.L
    LOCALE: ClassVar = _re.LOCALE
    M: ClassVar = _re.M
    MULTILINE: ClassVar = _re.MULTILINE
    S: ClassVar = _re.S
    DOTALL: ClassVar = _re.DOTALL
    U: ClassVar = _re.U
    UNICODE: ClassVar = _re.UNICODE
    X: ClassVar = _re.X
    VERBOSE: ClassVar = _re.VERBOSE

    def compile(self, pattern: str, flags: int = 0) -> object:
        """Compile `pattern` with the active engine (cached); use it with `pattern.*`."""

        try:
            return engine.compile(pattern, flags)
        except Exception as exc:  # re.error, regex.error, TypeError
            message = f"{type(exc).__name__}: {exc}"

            raise JinjaTypesError("re.compile", message, original=exc) from exc

    def __repr__(self) -> str:
        return "<jinja_types re flags>"


def _guard[T](name: str, call: Callable[[], T]) -> T:
    """Run `call`, turning any failure into a `JinjaTypesError` named `name`."""

    try:
        return call()
    except Exception as exc:  # ValueError, TypeError, IndexError
        raise JinjaTypesError(name, f"{type(exc).__name__}: {exc}", original=exc) from exc


class RandomNamespace:
    """The `random` global: the `random` module's functions on a private generator.

    The process-wide generator is never used, so templates cannot reseed it.
    `random.Random(seed)` returns a seeded generator with the same members.
    """

    def __init__(self, seed: int | str | None = None) -> None:
        self._rng = _random.Random(seed)

    def Random(self, seed: int | str | None = None) -> "RandomNamespace":
        """Return a new generator; with a `seed`, its sequence is repeatable."""
        return RandomNamespace(seed)

    def random(self) -> float:
        """Return a float in [0.0, 1.0)."""
        return self._rng.random()

    def uniform(self, a: float, b: float) -> float:
        """Return a float between `a` and `b`."""
        return _guard("random.uniform", lambda: self._rng.uniform(a, b))

    def randint(self, a: int, b: int) -> int:
        """Return an int in [a, b], both ends included."""
        return _guard("random.randint", lambda: self._rng.randint(a, b))

    def randrange(self, start: int, stop: int | None = None, step: int = 1) -> int:
        """Return an int from `range(start, stop, step)`."""
        return _guard("random.randrange", lambda: self._rng.randrange(start, stop, step))

    def choice[T](self, seq: Sequence[T]) -> T:
        """Return one element of a non-empty sequence."""
        return _guard("random.choice", lambda: self._rng.choice(seq))

    def choices[T](
        self,
        population: Sequence[T],
        weights: Sequence[float] | None = None,
        *,
        cum_weights: Sequence[float] | None = None,
        k: int = 1,
    ) -> list[T]:
        """Return `k` elements chosen with replacement, optionally weighted."""
        return _guard(
            "random.choices",
            lambda: self._rng.choices(population, weights, cum_weights=cum_weights, k=k),
        )

    def sample[T](
        self, population: Sequence[T], k: int, *, counts: Iterable[int] | None = None
    ) -> list[T]:
        """Return `k` distinct elements chosen without replacement."""
        return _guard("random.sample", lambda: self._rng.sample(population, k, counts=counts))

    def shuffle[T](self, x: Iterable[T]) -> list[T]:
        """Return a shuffled new list; the input is never changed."""

        items = list(x)

        self._rng.shuffle(items)

        return items

    def getrandbits(self, k: int) -> int:
        """Return an int with `k` random bits."""
        return _guard("random.getrandbits", lambda: self._rng.getrandbits(k))

    def gauss(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        """Return a float from a normal distribution."""
        return _guard("random.gauss", lambda: self._rng.gauss(mu, sigma))

    def __repr__(self) -> str:
        return "<jinja_types random>"


class SecretsNamespace:
    """The `secrets` global: cryptographically strong tokens (never seedable)."""

    def token_hex(self, nbytes: int | None = None) -> str:
        """Return a random hex string of `nbytes` bytes (2 digits per byte)."""
        return _guard("secrets.token_hex", lambda: _secrets.token_hex(nbytes))

    def token_urlsafe(self, nbytes: int | None = None) -> str:
        """Return a random URL-safe Base64 string of `nbytes` bytes."""
        return _guard("secrets.token_urlsafe", lambda: _secrets.token_urlsafe(nbytes))

    def choice[T](self, seq: Sequence[T]) -> T:
        """Return one element of a non-empty sequence."""
        return _guard("secrets.choice", lambda: _secrets.choice(seq))

    def randbelow(self, exclusive_upper_bound: int) -> int:
        """Return an int in [0, exclusive_upper_bound)."""
        return _guard("secrets.randbelow", lambda: _secrets.randbelow(exclusive_upper_bound))

    def __repr__(self) -> str:
        return "<jinja_types secrets>"


DECIMAL = DecimalNamespace()
RE_FLAGS = ReFlags()
RANDOM = RandomNamespace()
SECRETS = SecretsNamespace()


@collection.global_(
    member="decimal",
    constant=True,
    examples=[
        ("{{ decimal.Decimal('1.10') }}", {}, "1.10"),
        ("{{ decimal.ROUND_HALF_UP }}", {}, "ROUND_HALF_UP"),
    ],
)
def decimal_namespace() -> DecimalNamespace:
    """The `decimal` namespace object."""
    return DECIMAL


@collection.global_(
    member="re",
    constant=True,
    examples=[
        ("{{ re.I == 2 and re.IGNORECASE == re.I }}", {}, "True"),
        ("{{ re.compile('a+', re.I) | pattern.findall('aAb') | join }}", {}, "aA"),
    ],
)
def re_flags() -> ReFlags:
    """The `re` flags object, with `re.compile(pattern, flags=0)` for the `pattern` namespace."""
    return RE_FLAGS


@collection.global_(
    member="random",
    constant=True,
    examples=[
        ("{{ random.random() < 1 }}", {}, "True"),
        ("{{ random.Random(42).randint(1, 6) }}", {}, "6"),
        ("{{ random.Random(42).choice(['a', 'b', 'c']) }}", {}, "c"),
        ("{{ random.Random(42).shuffle([1, 2, 3, 4]) | join }}", {}, "3241"),
        ("{{ random.Random(42).sample(range(10), 3) | join }}", {}, "104"),
    ],
)
def random_namespace() -> RandomNamespace:
    """The `random` object; `random.Random(seed)` gives a repeatable generator."""
    return RANDOM


@collection.global_(
    member="secrets",
    constant=True,
    examples=[
        ("{{ secrets.token_hex(8) | length }}", {}, "16"),
        ("{{ secrets.randbelow(3) < 3 }}", {}, "True"),
    ],
)
def secrets_namespace() -> SecretsNamespace:
    """The `secrets` object: cryptographically strong tokens and choices."""
    return SECRETS


@collection.global_(examples=[("{{ today().year > 2000 }}", {}, "True")])
def today() -> date:
    """Return today's local date."""
    return date.today()


@collection.global_(
    examples=[
        ("{{ now().tzinfo }}", {}, "None"),
        ("{{ now(tz).utcoffset() }}", {"tz": UTC}, "0:00:00"),
    ]
)
def now(tz: tzinfo | None = None) -> datetime:
    """Return the current datetime, local or in `tz` (a `tzinfo`)."""
    return datetime.now(tz)


@collection.global_(
    examples=[
        (
            "{{ uuid5('6ba7b810-9dad-11d1-80b4-00c04fd430c8', 'example.com') }}",
            {},
            "cfbff0d1-9375-5685-968c-48ce8b15ae17",
        ),
        ("{{ uuid5(ns, 'example.com') | uuid.version }}", {"ns": NAMESPACE_DNS}, "5"),
    ]
)
def uuid5(namespace: UUID | str, name: str) -> UUID:
    """Return the name-based (SHA-1) UUID; same input, same UUID. `namespace` may be UUID text."""
    return _uuid5(namespace if isinstance(namespace, UUID) else UUID(namespace), name)


@collection.global_(examples=[("{{ uuid4() | uuid.version }}", {}, "4")])
def uuid4() -> UUID:
    """Return a random UUID (different on every call)."""
    return _uuid4()


@collection.global_(
    examples=[
        ("{{ uuid1() | uuid.version }}", {}, "1"),
        ("{{ uuid1(node=1) | uuid.node }}", {}, "1"),
    ]
)
def uuid1(node: int | None = None, clock_seq: int | None = None) -> UUID:
    """Return a time-based UUID; without `node`, a random node id is used, never the MAC."""

    # uuid.getnode() may start a subprocess and leaks the MAC; RFC 4122 §4.5 allows a random
    # node with the multicast bit set instead.
    if node is None:
        node = _random.getrandbits(48) | (1 << 40)

    return _uuid1(node, clock_seq)
