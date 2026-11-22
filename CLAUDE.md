# CLAUDE.md: jinja-types

`jinja-types` (import `jinja_types`) is a Jinja2 extension. It exposes Python type methods and attributes (str, int, float, bool, Decimal, Fraction, date, datetime, time, timedelta, list, dict, UUID, Path), plus the `re` module, as Jinja filters and tests. It is built around a **registry**, so new filter sets are easy to add (e.g. arapy for Arabic later). It is a hard dependency of **templify**, which renders templates in Python only.

Read `PHASES.md` for the build order. Work one phase at a time. A phase is done only when all of its acceptance criteria pass.

---

## Tooling

- Python **3.12+**. Use modern syntax: `type` aliases, PEP 695 generics, `match`, `X | Y`.
- **uv** for env and deps (`uv add`, `uv run`). Never call pip directly.
- **ruff** for lint and format (`uv run ruff check --fix && uv run ruff format`).
- **mypy --strict** must pass on `src/` and `tests/`.
- **pytest** (+ `pytest-cov`). Coverage target is ≥ 95% on `src/jinja_types/core`.
- Layout is `src/jinja_types/`. Ship `py.typed`.
- Runtime dependency: `jinja2>=3.1`. Optional extras: `[regex]` (regex library, timeouts) and `[babel]` (locale formatting).
- English docs and docstrings.

Before every commit run:

```
uv run ruff check --fix && uv run ruff format && uv run mypy && uv run pytest
```

---

## Core design rules (decided; do not change without asking)

1. **Qualified names only for type members.** Every type method or attribute is reachable only as `namespace.member`, e.g. `str.zfill`, `decimal.quantize`, `date.year`, `path.stem`, `re.sub`, `match.group`. There are no short aliases, so nothing can clash with Jinja built-ins (`count`, `format`, `join`, `max`, `min`, `replace`, …). Jinja's parser accepts dotted filter and test names; this was verified on Jinja 3.1.6.
2. **Names identical to Python.** The member name is the Python method or attribute name, and parameter names and order match Python. The piped value is always `self` (for `re.*`, the string being searched).
3. **Plain names for helpers.** Helpers that are not type members use plain names: `fmt`, `to_str`, `to_int`, `to_float`, `to_bool`, `to_decimal`, `to_fraction`, `to_date`, `to_datetime`, `to_time`, `to_timedelta`, `to_uuid`, `to_path`. The registry **raises** if a plain name collides with a Jinja built-in or with another plain name.
4. **Dispatch within subclasses only.** `date.strftime` applied to a `datetime` value calls `datetime.strftime` if it is registered. The registry walks the value's MRO up to the namespace type and uses the most specific match. A value that is not an instance of the namespace type raises `JinjaTypesError`. Note that `bool` is a subclass of `int`, so `int.*` accepts `True`; this is documented.
5. **Small typed wrappers.** Each filter is a small, fully annotated function that calls the real method. Builtin methods have no annotations, and some have no signature (`str.count`, `date.strftime`, …), so the catalog's types come **only** from our wrappers. Do not use `inspect` on builtins for metadata.
6. **Predicates become tests.** A wrapper whose return annotation is `bool` is registered as a filter **and** a test (`{% if code is str.isdigit %}`). `re.search`/`re.match`/`re.fullmatch` are registered as tests explicitly; the test is true when a match is found.
7. **Mutating methods work on copies.** `list.append/extend/insert/remove/reverse/sort/clear` and `dict.update/clear` return a **new** object and never mutate the input. `list.pop`, `dict.pop`, `dict.popitem` and `dict.setdefault` return Python's return value (the item), computed on a copy. A generic test asserts that inputs are never mutated.
8. **Classmethods become parsing filters.** `date.fromisoformat`, `datetime.strptime(fmt)`, `datetime.fromtimestamp`, `int.from_bytes`, `fraction.from_decimal`, … take the piped value as their first argument. They live next to the friendly `to_*` helpers.
9. **Constants are globals only.** Templates get namespace objects as globals: `decimal` (`decimal.Decimal`, `decimal.ROUND_HALF_UP`, …), `re` (flags only: `re.I`, `re.M`, `re.S`, `re.X`, `re.A`, …), plus `today()` and `now()`. Globals and filters are separate Jinja namespaces, so the global `decimal` and the filter `decimal.quantize` coexist.
10. **Pure paths only.** The `path.*` namespace exposes only `PurePath` members, never anything that touches the disk.
11. **Strict by default.** `None` or `""` input raises `JinjaTypesError`. The option `none_passthrough=True` returns such values unchanged.
12. **Explicit conversion, opt-in coercion.** By default, string input must be converted (`| to_date`, `| date.fromisoformat`). The option `coerce=True` converts a `str` to the namespace type using that namespace's `parse` function before calling the member.
13. **One error type.** Every failure raises `JinjaTypesError`, a subclass of `jinja2.TemplateRuntimeError`. It carries the filter name, the value's type, the supported types, the original exception, and a **hint**. Example: `date.strftime: got 'str', expected date | datetime. Hint: convert first with '| to_date' or '| date.fromisoformat'.`
14. **Regex.** The piped value is the string. Engine is stdlib `re` by default; `[regex]` switches to the `regex` library with `regex_timeout=1.0` (configurable; a timeout raises `JinjaTypesError`). `re.sub`/`re.subn` accept a string replacement or a **Jinja macro** taking the Match; the macro result must be converted to plain `str` so autoescape works once. `re.compile` is not in v1.
15. **Sandbox-safe.** Everything must work in `ImmutableSandboxedEnvironment`, which is what templify uses. Never expose callables that touch the filesystem, network, or process.

---

## Architecture: the registry pattern

```
src/jinja_types/
  __init__.py          # public API re-exports
  py.typed
  core/
    spec.py            # Kind, Param, MemberSpec (frozen dataclasses)
    namespace.py       # Namespace(name, type, parse=None)
    collection.py      # Collection: decorators that build MemberSpecs
    registry.py        # Registry: include/merge, conflicts, lookup, dispatch
    invoker.py         # call pipeline: passthrough → coerce → dispatch → call → error translation
    options.py         # Options (frozen): none_passthrough, coerce, regex_timeout, locale…
    errors.py          # JinjaTypesError, RegistryError, DuplicateMemberError, BuiltinClashError
    catalog.py         # Catalog / CatalogEntry + JSON export
    plugins.py         # entry-point discovery ("jinja_types.plugins")
  extension.py         # TypesExtension, install(env, …)
  helpers/             # fmt, to_* converters, globals (decimal, re flags, today, now)
  types/               # one module per namespace: str_.py, int_.py, float_.py, bool_.py,
                       #   decimal_.py, fraction_.py, date_.py, datetime_.py, time_.py,
                       #   timedelta_.py, list_.py, dict_.py, uuid_.py, path_.py
  regex/               # re_.py (module functions), match_.py (Match members), engine.py
  contrib/babel.py     # [babel] extra: babel.format_decimal, babel.format_currency, babel.format_date…
  cli.py               # `jinja-types catalog …` (argparse, no extra deps)
```

### Concepts

- **`Namespace`** is a name and a Python type, with an optional `parse(str) -> T` used by `coerce=True`. Built-in namespaces: `str int float bool decimal fraction date datetime time timedelta list dict uuid path re match`. `re` is a *module namespace*: its value type is `str`. The helper namespace is `None`, which gives plain names.
- **`MemberSpec`** (frozen) has these fields: `name` (qualified), `namespace`, `member`, `func`, `kinds` (`FILTER`, `TEST`, `ATTRIBUTE`, `GLOBAL`), `params: tuple[Param, …]`, `returns`, `doc`, `examples`, `source` (`"jinja_types"` or the plugin name). It is built from the wrapper's signature and type hints **at registration time**.
- **`Collection`** is a bag of specs for one namespace, filled with decorators. Each `types/*.py` module exports exactly one collection. This is the unit that plugins provide.
- **`Registry`** combines collections. It enforces the conflict rules, owns the dispatch tables, produces the catalog, and installs itself into an `Environment`.
- **`Invoker`** is what Jinja actually calls. It wraps every spec in one place, so options, dispatch and error translation are not repeated across ~250 wrappers.

### Writing a collection

```python
# src/jinja_types/types/decimal_.py
from decimal import Decimal
from jinja_types.core import Collection

collection = Collection(namespace="decimal", type=Decimal, parse=Decimal)


@collection.filter(
    examples=[
        ("{{ x | decimal.quantize(decimal.Decimal('0.01')) }}", {"x": Decimal("1.005")}, "1.00")
    ]
)
def quantize(value: Decimal, exp: Decimal, /, rounding: str | None = None) -> Decimal:
    """Return `value` rounded to the exponent of `exp`."""
    return value.quantize(exp, rounding=rounding)


@collection.filter(examples=[("{{ x | decimal.is_signed }}", {"x": Decimal("-1")}, "True")])
def is_signed(value: Decimal, /) -> bool:  # bool return → also a test
    """Return True if the sign is negative."""
    return value.is_signed()


@collection.attribute(examples=[("{{ x | decimal.real }}", {"x": Decimal("2.5")}, "2.5")])
def real(value: Decimal, /) -> Decimal:
    """The real part (the value itself)."""
    return value.real
```

Conventions for wrappers:
- The function name equals the Python member name. If it clashes with a Python keyword or builtin, use a trailing underscore and pass `member="…"`.
- The first parameter is `value`, positional-only, annotated with the namespace type.
- Mirror Python's positional-only and keyword parameters exactly.
- The body is one line that calls the real member. Add copy logic only for mutating methods (rule 7).
- Every wrapper has a one-line docstring and **at least one example**. Examples are `(template, context, expected_output)` and are run by `tests/test_examples.py` for every spec in the default registry. A spec without examples fails the test suite.

### Registering and installing

```python
from jinja2.sandbox import ImmutableSandboxedEnvironment
from jinja_types import Registry, TypesExtension, install

registry = Registry.default()  # all built-in collections
registry.include(my_collection)  # raises DuplicateMemberError on a clash
registry.include(other, replace=True)  # explicit override
registry.load_plugins()  # entry points in group "jinja_types.plugins"

env = ImmutableSandboxedEnvironment(
    extensions=[TypesExtension.configure(registry=registry, none_passthrough=True)],
)
# or: install(env, registry=registry, coerce=True)
```

`TypesExtension.configure(**options)` returns a configured subclass, because Jinja constructs extensions with only `environment`. With no configuration, `TypesExtension` uses `Registry.default()` and default `Options`.

### Conflict rules (enforced in `Registry.include`)

| Situation | Result |
|---|---|
| Same qualified name twice | `DuplicateMemberError`, unless `replace=True` |
| Plain-name helper equals a Jinja built-in filter/test | `BuiltinClashError` (checked against the target env at install) |
| Same member on a parent and a child namespace (`date.replace` / `datetime.replace`) | Both kept; MRO dispatch picks the most specific |
| A plugin redefines a built-in spec | Needs `replace=True`; the catalog records `source` and `replaced` |

`registry.conflicts()` returns every resolution decision for docs and for templify.

### Plugins

A third-party package exposes collections through an entry point:

```toml
[project.entry-points."jinja_types.plugins"]
arapy = "arapy.jinja:collections"      # a Collection or an iterable of Collections
```

Plugins are loaded only when `load_plugins()` is called, or with `Registry.default(plugins=True)`. Loading stays explicit so templify renders deterministically.

### Catalog

`registry.catalog()` returns typed `CatalogEntry` objects with these fields: name, kinds, namespace, input type, params (name, kind, annotation, default), returns, doc, examples, source. `Catalog.to_json()` and `jinja-types catalog [--namespace X] [--format json|markdown]` export it. templify uses it for autocomplete, and the docs are generated from it.

---

## Testing rules

- `tests/test_examples.py` runs every spec's examples in an `ImmutableSandboxedEnvironment`, with autoescape on and off.
- `tests/test_no_mutation.py` deep-copies the inputs of every list/dict spec's examples and asserts they are unchanged after rendering.
- `tests/test_parity.py` checks, for every type-member spec, that the wrapper's output equals calling the real Python member directly with the same arguments.
- `tests/test_catalog.py` asserts that every spec has a docstring, ≥1 example, and complete annotations.
- Core tests cover dispatch, conflicts, options, errors and hints, and plugin loading (using a fake entry point).

---

## Deferred / out of scope for v1

- Arabic filters: these come from **arapy** as a plugin once arapy is finished.
- `re.compile` and Pattern members.
- A JS or browser port. templify renders in Python only; the JSON catalog keeps a port possible.
- Locale formatting beyond the `[babel]` extra.

## Decided: wrappers are written by hand

- The ~250 wrappers are written by hand, namespace by namespace (decided 2026-11-22). No generator script.
