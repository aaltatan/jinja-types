"""Render-time options."""

from contextvars import ContextVar
from dataclasses import dataclass
from typing import TypedDict


@dataclass(frozen=True, slots=True)
class Options:
    """Options that change how every jinja-types member behaves."""

    none_passthrough: bool = False
    coerce: bool = False
    regex_timeout: float = 1.0
    locale: str | None = None


class OptionsKwargs(TypedDict, total=False):
    """Keyword form of `Options`, for `install(...)` and `TypesExtension.configure(...)`."""

    none_passthrough: bool
    coerce: bool
    regex_timeout: float
    locale: str | None


CURRENT: ContextVar[Options] = ContextVar("jinja_types_options", default=Options())  # noqa: B039 (frozen)
"""The options of the install running the current member, for wrappers that need them (regex)."""
