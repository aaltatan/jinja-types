"""The call pipeline Jinja runs for every member.

passthrough → coerce → isinstance check → MRO dispatch → call → error translation
"""

from collections.abc import Callable, Mapping

from jinja2 import TemplateError, Undefined

from .errors import JinjaTypesError
from .options import Options
from .registry import Registry
from .spec import MemberSpec

MARK = "__jinja_types_spec__"
"""Attribute set on every installed callable, so a re-install does not see a clash."""

# Converters suggested when a value has the wrong type for a namespace.
CONVERTERS: dict[str, tuple[str, ...]] = {
    "str": ("to_str",),
    "int": ("to_int",),
    "float": ("to_float",),
    "bool": ("to_bool",),
    "decimal": ("to_decimal",),
    "fraction": ("to_fraction",),
    "date": ("to_date", "date.fromisoformat"),
    "datetime": ("to_datetime", "datetime.fromisoformat"),
    "time": ("to_time", "time.fromisoformat"),
    "timedelta": ("to_timedelta",),
    "uuid": ("to_uuid",),
    "path": ("to_path",),
}

NONE_HINT = "pass a value, or install with none_passthrough=True"


def type_hint(namespace: str, supported: tuple[str, ...]) -> str:
    """Return the hint for a value of the wrong type."""

    converters = CONVERTERS.get(namespace)

    if converters is None:
        return f"pass a {' | '.join(supported)} value"

    return "convert first with " + " or ".join(f"'| {name}'" for name in converters)


def signature(spec: MemberSpec) -> str:
    """Return `name(param: type = default, ...)` for hints."""

    params = [
        f"{p.name}: {p.annotation}" + ("" if p.default is None else f" = {p.default}")
        for p in spec.params
    ]

    return f"{spec.name}({', '.join(params)})"


def is_missing(value: object) -> bool:
    """`None`, `""` and Jinja `Undefined` count as missing."""

    return value is None or isinstance(value, Undefined) or (isinstance(value, str) and not value)


def describe(value: object) -> str:
    if isinstance(value, Undefined):
        return "an undefined value"

    if value is None:
        return "None"

    return "an empty string"


class Invoker:
    """Builds the callables installed into a Jinja environment."""

    def __init__(self, registry: Registry, options: Options) -> None:
        self.registry = registry
        self.options = options

    def filter(self, spec: MemberSpec) -> Callable[..., object]:
        def jinja_filter(value: object, /, *args: object, **kwargs: object) -> object:
            return self.call(spec, value, args, kwargs)

        setattr(jinja_filter, MARK, spec)

        return jinja_filter

    def test(self, spec: MemberSpec) -> Callable[..., bool]:
        def jinja_test(value: object, /, *args: object, **kwargs: object) -> bool:
            return bool(self.call(spec, value, args, kwargs))

        setattr(jinja_test, MARK, spec)

        return jinja_test

    def global_(self, spec: MemberSpec) -> Callable[..., object]:
        def jinja_global(*args: object, **kwargs: object) -> object:
            return self.run(spec, spec, args, kwargs)

        setattr(jinja_global, MARK, spec)

        return jinja_global

    def call(
        self,
        spec: MemberSpec,
        value: object,
        args: tuple[object, ...],
        kwargs: Mapping[str, object],
    ) -> object:
        """Run the full pipeline for a piped value."""

        namespace = spec.namespace
        supported = () if namespace.name is None else self.registry.supported(namespace)

        if is_missing(value):
            if self.options.none_passthrough:
                return value

            raise JinjaTypesError(
                spec.name,
                f"got {describe(value)}",
                value_type=type(value).__name__,
                supported=supported,
                hint=NONE_HINT,
            )

        if namespace.name is None or spec.classmethod:
            return self.run(spec, spec, (value, *args), kwargs)

        parse = self.registry.namespace(namespace.name).parse

        if (
            self.options.coerce
            and parse is not None
            and isinstance(value, str)
            and not isinstance(value, namespace.type)
        ):
            try:
                value = parse(value)
            except Exception as exc:
                raise JinjaTypesError(
                    spec.name,
                    f"could not convert {value!r} to {namespace.type.__name__}: {exc}",
                    value_type="str",
                    supported=supported,
                    hint=type_hint(namespace.name, supported),
                    original=exc,
                ) from exc

        if not isinstance(value, namespace.type):
            raise JinjaTypesError(
                spec.name,
                f"got {type(value).__name__!r}, expected {' | '.join(supported)}",
                value_type=type(value).__name__,
                supported=supported,
                hint=type_hint(namespace.name, supported),
            )

        return self.run(spec, self.registry.resolve(spec, value), (value, *args), kwargs)

    def run(
        self,
        spec: MemberSpec,
        target: MemberSpec,
        args: tuple[object, ...],
        kwargs: Mapping[str, object],
    ) -> object:
        """Call `target` and translate any non-Jinja exception into `JinjaTypesError`."""

        typed = spec.namespace.name is not None
        hint = f"check the arguments: {signature(target)}"

        try:
            return target.func(*args, **kwargs)
        except TemplateError:
            raise
        except Exception as exc:
            raise JinjaTypesError(
                spec.name,
                f"{type(exc).__name__}: {exc}",
                value_type=type(args[0]).__name__ if args and target.input_type else None,
                supported=self.registry.supported(spec.namespace) if typed else (),
                hint=hint if isinstance(exc, TypeError) else None,
                original=exc,
            ) from exc
