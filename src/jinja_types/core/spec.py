"""Member specs: the typed description of one filter, test, attribute or global."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Flag, auto

from .namespace import Namespace

type Example = tuple[str, Mapping[str, object], str]
"""`(template, context, expected_output)`."""


class Kind(Flag):
    """How a member is exposed to Jinja."""

    FILTER = auto()
    TEST = auto()
    ATTRIBUTE = auto()
    GLOBAL = auto()


@dataclass(frozen=True, slots=True)
class Param:
    """One wrapper parameter, as shown in the catalog."""

    name: str
    kind: str
    annotation: str
    default: str | None = None
    """`repr()` of the default value, or `None` when the parameter is required."""


@dataclass(frozen=True, slots=True)
class MemberSpec:
    """Everything known about one registered member."""

    name: str
    namespace: Namespace
    member: str
    func: Callable[..., object]
    kinds: Kind
    params: tuple[Param, ...]
    input_type: str | None
    returns: str
    doc: str
    examples: tuple[Example, ...]
    source: str = "jinja_types"
    replaced: bool = False
    constant: bool = False
    """A global whose value is `func()` rather than `func` itself."""
