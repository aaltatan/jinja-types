"""Namespaces: a name plus the Python type its members accept."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Namespace:
    """A filter namespace such as `date`, bound to a Python type.

    `name=None` is the helper namespace: its members get plain names (`fmt`, `to_int`).
    `parse` converts a `str` to `type` when the `coerce` option is on.
    """

    name: str | None
    type: type
    parse: Callable[[str], object] | None = None

    def qualify(self, member: str) -> str:
        """Return the name a member is registered under (`date.year` or `fmt`)."""
        return member if self.name is None else f"{self.name}.{member}"
