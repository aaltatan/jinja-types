# API

Everything below is importable from `jinja_types`.

## TypesExtension

```python
class TypesExtension(jinja2.ext.Extension)
```

Installs the registry's filters, tests and globals into the environment it is added to. Uses
`Registry.default()` and default `Options` unless configured. Also usable as the string
`"jinja_types.TypesExtension"`.

`TypesExtension.configure(registry=None, *, none_passthrough=False, coerce=False, regex_timeout=1.0, locale=None) -> type[TypesExtension]`
:   Return a subclass bound to `registry` and the [options](#options). Jinja passes only the
    environment to an extension, so this is how options reach it.

## install

```python
def install(env, registry=None, *, options=None, **kwargs) -> Registry
```

Register every filter, test and global of `registry` (default `Registry.default()`) in `env`.
`kwargs` override fields of `options`. Raises `BuiltinClashError`, before changing anything, if
a plain-name helper is already a different filter, test or global in `env`. This is the plumbing
`TypesExtension` calls; applications add the extension instead.

## Options

```python
@dataclass(frozen=True)
class Options:
    none_passthrough: bool = False
    coerce: bool = False
    regex_timeout: float = 1.0
    locale: str | None = None
```

See [Setup and options](../guide/setup.md#options).

## Registry

All known members, keyed by qualified name.

| Method | Description |
|---|---|
| `Registry.default(*, plugins=False)` | Every built-in collection, plus plugins if asked. |
| `include(*collections, replace=False, source=None)` | Add collections; all or nothing. Returns the registry. |
| `load_plugins(group="jinja_types.plugins")` | Include every collection exposed by entry points. Returns the registry. |
| `get(name)` | The `MemberSpec` under `name`, or `KeyError`. |
| `name in registry` | Whether a member is registered. |
| `specs()` | All specs, sorted by name. |
| `namespaces()` / `namespace(name)` | The named namespaces / one of them (`KeyError` if unknown). |
| `conflicts()` | Every `Conflict` (replacements and parent/child dispatch). |
| `resolve(spec, value)` | The most specific spec for `value`, walking its MRO. |
| `supported(namespace)` | The type names a namespace accepts (its type plus registered subclasses). |
| `catalog()` | The typed `Catalog`. |
| `copy()` | An independent copy. |

## Conflict

```python
@dataclass(frozen=True)
class Conflict:
    name: str
    resolution: Literal["replaced", "dispatch"]
    detail: str
```

## Collection

```python
Collection(namespace=None, type=object, parse=None, *, source="jinja_types")
```

A set of member specs for one namespace. `namespace=None` holds plain-name helpers. `parse`
converts a `str` to `type` when `coerce=True`. Iterate it for its `MemberSpec`s.

| Decorator | Registers |
|---|---|
| `filter(*, member=None, examples=(), test=None)` | A filter; also a test if it returns `bool` (or `test=True`). |
| `test(*, member=None, examples=())` | A test only. |
| `attribute(*, member=None, examples=())` | An argument-less filter for a property. |
| `classmethod(*, member=None, examples=())` | A parsing filter; the piped value is not type-checked. |
| `global_(*, member=None, examples=(), constant=False)` | A global (helper namespace only); with `constant=True` the global is the function's return value. |

`member` overrides the name (for Python keywords and builtins). `examples` are
`(template, context, expected_output)` tuples. See [Writing a plugin](../guide/plugins.md).

## Namespace

```python
@dataclass(frozen=True)
class Namespace:
    name: str | None
    type: type
    parse: Callable[[str], object] | None = None

    def qualify(self, member: str) -> str: ...   # "date.year", or "fmt" when name is None
```

## Kind

`Flag` enum: `FILTER`, `TEST`, `ATTRIBUTE`, `GLOBAL`.

## MemberSpec and Param

`MemberSpec` (frozen) describes one registered member: `name`, `namespace`, `member`, `func`,
`kinds`, `params`, `input_type`, `returns`, `doc`, `examples`, `source`, `replaced`, `constant`,
`classmethod`.

`Param` (frozen) is one wrapper parameter: `name`, `kind` (`positional_only`, `var_keyword`, …),
`annotation`, and `default` (the `repr()` of the default, or `None` when required).

## Catalog and CatalogEntry

`Catalog` is an iterable, sized collection of `CatalogEntry` objects (the same fields as
`MemberSpec`, without the callable; `kinds` are lower-case strings).

| Method | Description |
|---|---|
| `select(*, namespace=None, kind=None)` | Entries in a namespace label and with a kind. |
| `namespaces()` | Namespace labels in use, sorted (`helpers` for plain names). |
| `to_dict()` / `to_json(*, indent=2)` | Plain data / JSON; see [Catalog and CLI](catalog.md). |
| `to_markdown()` | One `#` section per namespace, one `##` section per member. |

## Exceptions

`JinjaTypesError`, `RegistryError`, `DuplicateMemberError`, `BuiltinClashError`: see
[Exceptions](exceptions.md).
