"""Render-time options."""

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
