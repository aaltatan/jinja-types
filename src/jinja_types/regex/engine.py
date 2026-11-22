"""The regex engine: stdlib `re`, or the `regex` library when the `[regex]` extra is installed.

With `regex`, every call gets `timeout=regex_timeout` from the current install's options, and a
timeout raises `TimeoutError`, which the invoker turns into a `JinjaTypesError` with a hint.
Pattern errors (`re.error`, with the position in its message) are translated the same way.
"""

import importlib
import re
from abc import ABC
from types import ModuleType
from typing import Any

from jinja_types.core import CURRENT

try:
    regex: ModuleType | None = importlib.import_module("regex")  # untyped library
except ImportError:  # the [regex] extra is not installed
    regex = None


class Match(ABC):  # noqa: B024 (only a marker: re.Match and regex.Match share no base class)
    """Any match object of the active engine."""


Match.register(re.Match)

if regex is not None:
    Match.register(regex.Match)


def call(function: str, /, *args: object, **kwargs: object) -> Any:  # noqa: ANN401 (engine result)
    """Call `function` of the active engine, with the configured timeout under `regex`."""

    if regex is None:
        return getattr(re, function)(*args, **kwargs)

    return getattr(regex, function)(*args, timeout=CURRENT.get().regex_timeout, **kwargs)
