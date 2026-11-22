"""Errors raised by jinja-types."""

from jinja2 import TemplateRuntimeError


class JinjaTypesError(TemplateRuntimeError):
    """A jinja-types filter, test or global failed while rendering."""

    def __init__(
        self,
        filter_name: str,
        message: str,
        *,
        value_type: str | None = None,
        supported: tuple[str, ...] = (),
        hint: str | None = None,
        original: BaseException | None = None,
    ) -> None:
        text = f"{filter_name}: {message}."

        if hint:
            text += f" Hint: {hint}."

        super().__init__(text)

        self.filter_name = filter_name
        self.value_type = value_type
        self.supported = supported
        self.hint = hint
        self.original = original


class RegistryError(Exception):
    """A collection or registry was set up incorrectly."""


class DuplicateMemberError(RegistryError):
    """The same qualified name was registered twice without `replace=True`."""


class BuiltinClashError(RegistryError):
    """A plain-name helper has the same name as an existing Jinja filter, test or global."""
