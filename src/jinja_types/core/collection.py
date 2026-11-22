"""Collections: decorators that turn typed wrappers into member specs."""

import builtins
import inspect
import typing
from collections.abc import Callable, Iterable, Iterator
from types import NoneType, UnionType

from .errors import DuplicateMemberError, RegistryError
from .namespace import Namespace
from .spec import Example, Kind, MemberSpec, Param


def type_repr(hint: object) -> str:
    """Render a type hint the way it is written in source (`str | None`, `list[int]`)."""

    if hint is None or hint is NoneType:
        return "None"

    if hint is Ellipsis:
        return "..."

    if isinstance(hint, list):
        return "[" + ", ".join(type_repr(arg) for arg in hint) + "]"

    origin = typing.get_origin(hint)
    args = typing.get_args(hint)

    if origin is typing.Union or origin is UnionType:
        return " | ".join(type_repr(arg) for arg in args)

    if origin is typing.Literal:
        return "Literal[" + ", ".join(repr(arg) for arg in args) + "]"

    if origin is not None and args:
        return f"{type_repr(origin)}[{', '.join(type_repr(arg) for arg in args)}]"

    if isinstance(hint, builtins.type):
        return hint.__name__

    return repr(hint).removeprefix("typing.").removeprefix("collections.abc.")


def build_spec(
    namespace: Namespace,
    func: Callable[..., object],
    kind: Kind,
    *,
    member: str | None = None,
    examples: Iterable[Example] = (),
    test: bool | None = None,
    source: str = "jinja_types",
) -> MemberSpec:
    """Build a spec from a wrapper's own signature and type hints."""

    member = member or func.__name__
    name = namespace.qualify(member)

    try:
        hints = typing.get_type_hints(func)
    except Exception as exc:
        raise RegistryError(f"{name}: cannot resolve type hints: {exc}") from exc

    params = list(inspect.signature(func).parameters.values())
    missing = [p.name for p in params if p.name not in hints]

    if "return" not in hints:
        missing.append("return")

    if missing:
        raise RegistryError(f"{name}: missing annotations for {', '.join(missing)}")

    input_type: str | None = None

    if kind is Kind.GLOBAL:
        if namespace.name is not None:
            raise RegistryError(f"{name}: globals belong in the helper namespace (namespace=None)")

    else:
        if not params or params[0].kind is not inspect.Parameter.POSITIONAL_ONLY:
            raise RegistryError(f"{name}: the first parameter (the value) must be positional-only")

        first, *params = params
        input_type = type_repr(hints[first.name])

        if kind is Kind.ATTRIBUTE and params:
            raise RegistryError(f"{name}: an attribute takes no arguments besides the value")

    kinds = kind

    if kind in Kind.FILTER | Kind.ATTRIBUTE and (hints["return"] is bool if test is None else test):
        kinds |= Kind.TEST

    return MemberSpec(
        name=name,
        namespace=namespace,
        member=member,
        func=func,
        kinds=kinds,
        params=tuple(
            Param(
                name=p.name,
                kind=p.kind.name.lower(),
                annotation=type_repr(hints[p.name]),
                default=None if p.default is p.empty else repr(p.default),
            )
            for p in params
        ),
        input_type=input_type,
        returns=type_repr(hints["return"]),
        doc=inspect.getdoc(func) or "",
        examples=tuple(examples),
        source=source,
    )


class Collection:
    """A bag of member specs for one namespace, filled with decorators.

    `Collection("date", date, parse=date.fromisoformat)` holds `date.*` members;
    `Collection()` holds plain-name helpers.
    """

    def __init__(
        self,
        namespace: str | None = None,
        type: builtins.type = object,
        parse: Callable[[str], object] | None = None,
        *,
        source: str = "jinja_types",
    ) -> None:
        self.namespace = Namespace(namespace, type, parse)
        self.source = source
        self._specs: dict[str, MemberSpec] = {}

    def __iter__(self) -> Iterator[MemberSpec]:
        return iter(self._specs.values())

    def __len__(self) -> int:
        return len(self._specs)

    def __repr__(self) -> str:
        return f"Collection({self.namespace.name!r}, {len(self)} members)"

    def filter[F: Callable[..., object]](
        self,
        *,
        member: str | None = None,
        examples: Iterable[Example] = (),
        test: bool | None = None,
    ) -> Callable[[F], F]:
        """Register a filter. It is also a test if it returns `bool` (or `test=True`)."""

        return self._register(Kind.FILTER, member, examples, test)

    def test[F: Callable[..., object]](
        self, *, member: str | None = None, examples: Iterable[Example] = ()
    ) -> Callable[[F], F]:
        """Register a test only."""

        return self._register(Kind.TEST, member, examples, None)

    def attribute[F: Callable[..., object]](
        self, *, member: str | None = None, examples: Iterable[Example] = ()
    ) -> Callable[[F], F]:
        """Register an attribute, used as an argument-less filter (`{{ d | date.year }}`)."""

        return self._register(Kind.ATTRIBUTE, member, examples, None)

    def global_[F: Callable[..., object]](
        self, *, member: str | None = None, examples: Iterable[Example] = ()
    ) -> Callable[[F], F]:
        """Register a global callable (helper namespace only)."""

        return self._register(Kind.GLOBAL, member, examples, None)

    def _register[F: Callable[..., object]](
        self, kind: Kind, member: str | None, examples: Iterable[Example], test: bool | None
    ) -> Callable[[F], F]:
        def register(func: F) -> F:
            spec = build_spec(
                self.namespace,
                func,
                kind,
                member=member,
                examples=examples,
                test=test,
                source=self.source,
            )

            if spec.name in self._specs:
                raise DuplicateMemberError(f"{spec.name} is defined twice in {self!r}")

            self._specs[spec.name] = spec

            return func

        return register
