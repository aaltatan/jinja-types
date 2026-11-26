# Writing a jinja-types plugin

A plugin is a Python package that adds filters and tests to jinja-types through an entry point.
This guide builds `acme-jinja`, which adds an `iban` namespace:

```jinja
{{ account | iban.format }}            {# GB82 WEST 1234 5698 7654 32 #}
{% if account is iban.is_valid %}…{% endif %}
```

## 1. The collection

A `Collection` holds the members of one namespace. Each decorated function becomes one member,
and the function name is the member name.

```python
# src/acme_jinja/iban.py
"""The `iban` namespace: format and check International Bank Account Numbers."""

from jinja_types import Collection

collection = Collection("iban", str)

GB = "GB82 west 1234 5698 7654 32"


@collection.filter(examples=[("{{ code | iban.compact }}", {"code": GB}, "GB82WEST12345698765432")])
def compact(value: str, /) -> str:
    """Return the IBAN without spaces, in upper case."""
    return value.replace(" ", "").upper()


@collection.filter(
    member="format",
    examples=[
        ("{{ code | iban.format }}", {"code": GB}, "GB82 WEST 1234 5698 7654 32"),
        ("{{ code | iban.format('-') }}", {"code": "GB82WEST1234"}, "GB82-WEST-1234"),
    ],
)
def format_(value: str, /, sep: str = " ") -> str:
    """Return the IBAN in groups of four characters."""
    code = compact(value)

    return sep.join(code[i : i + 4] for i in range(0, len(code), 4))


@collection.filter(
    examples=[
        ("{{ code is iban.is_valid }}", {"code": GB}, "True"),
        ("{{ 'GB00WEST1234' is iban.is_valid }}", {}, "False"),
    ]
)
def is_valid(value: str, /) -> bool:  # returns bool, so it is also a test
    """Return True if the IBAN's check digits are right (ISO 13616, mod 97)."""
    code = compact(value)

    if not code.isalnum() or len(code) < 5:
        return False

    digits = "".join(str(int(char, 36)) for char in code[4:] + code[:4])  # A=10 ... Z=35

    return int(digits) % 97 == 1
```

`Collection(namespace, type, parse=None)`:

- `namespace` is the prefix of every member (`iban.format`). Use `None` for plain-name helpers.
  Plain names must not clash with Jinja's built-in filters and tests, or installing fails with
  `BuiltinClashError`.
- `type` is the type the piped value must have. Any other type raises `JinjaTypesError`, with a
  hint listing the supported types.
- `parse` turns a string into `type` when the environment is configured with `coerce=True`.

The decorators are:

| Decorator | Template use | Notes |
|---|---|---|
| `@collection.filter()` | `{{ x | ns.name(...) }}` | A `bool` return also registers a test; pass `test=False` to opt out. |
| `@collection.test()` | `{% if x is ns.name %}` | A test only. |
| `@collection.attribute()` | `{{ x | ns.name }}` | A property, no arguments. |
| `@collection.classmethod()` | `{{ "2026-01-05" | ns.name }}` | Parses the piped value, which is not type-checked. |
| `@collection.global_()` | `{{ name(...) }}` | A function global. With `constant=True`, the global is the object it returns. |

Conventions, the same ones jinja-types follows:

- The first parameter is `value`, positional-only (`/`), and annotated with the namespace type.
- Annotate every parameter and the return type: the catalog (autocomplete, docs) is built from
  them.
- Write a one-line docstring and at least one `(template, context, expected)` example. Examples
  must render the same with autoescape on and off.
- If a member name clashes with a Python keyword or builtin, add a trailing underscore and pass
  `member="..."` (`format_` above).
- Return new values. Never mutate the input, and never touch the filesystem, network or
  processes: everything must be safe in `ImmutableSandboxedEnvironment`.
- Let exceptions propagate. jinja-types turns them into `JinjaTypesError`, with the member name.

## 2. The entry point

Expose the collection (or a list of collections) in the `jinja_types.plugins` group:

```toml
# pyproject.toml
[project]
name = "acme-jinja"
dependencies = ["jinja-types>=0.1.0"]

[project.entry-points."jinja_types.plugins"]
acme = "acme_jinja.iban:collection"
```

The entry point name (`acme`) becomes the `source` of every member in the catalog.

## 3. Using it

Plugins are loaded only on request, so a render never changes because a package happened to be
installed:

```python
from jinja2.sandbox import ImmutableSandboxedEnvironment
from jinja_types import Registry, TypesExtension

registry = Registry.default(plugins=True)  # or: Registry.default(); registry.load_plugins()

env = ImmutableSandboxedEnvironment(extensions=[TypesExtension.configure(registry=registry)])
```

To include a collection without an entry point, for example in a project's own code:

```python
from acme_jinja.iban import collection

registry = Registry.default()
registry.include(collection, source="acme")
```

A plugin that redefines an existing member (`str.title`, for example) fails with
`DuplicateMemberError`. Overriding it is an explicit choice:
`registry.include(collection, replace=True)`. The catalog then marks the member as `replaced`.
`jinja-types conflicts --plugins` lists every such decision, and
`jinja-types catalog --plugins --namespace iban` shows the plugin's members.

## 4. Testing the examples

Run every example the way jinja-types runs its own:

```python
import pytest
from jinja2.sandbox import ImmutableSandboxedEnvironment
from jinja_types import Registry, TypesExtension

from acme_jinja.iban import collection

registry = Registry.default()
registry.include(collection, source="acme")

CASES = [example for spec in collection for example in spec.examples]


@pytest.mark.parametrize("autoescape", [False, True])
@pytest.mark.parametrize(("template", "context", "expected"), CASES)
def test_examples(
    template: str, context: dict[str, object], expected: str, autoescape: bool
) -> None:
    extension = TypesExtension.configure(registry=registry)
    env = ImmutableSandboxedEnvironment(autoescape=autoescape, extensions=[extension])

    assert env.from_string(template).render(**context) == expected
```
