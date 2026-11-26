# Setup and options

## Add the extension

jinja-types is a Jinja extension. Add it to your environment:

```python
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import TypesExtension

env = ImmutableSandboxedEnvironment(extensions=[TypesExtension])
```

The string `"jinja_types.TypesExtension"` works too, wherever Jinja takes extension names.
Everything works in `ImmutableSandboxedEnvironment`, and a plain `Environment` works the same.

## Options

Jinja constructs extensions with only the environment, so options go through
`TypesExtension.configure(...)`, which returns a configured subclass:

```python
env = ImmutableSandboxedEnvironment(
    extensions=[TypesExtension.configure(none_passthrough=True, locale="ar_SY")],
)
```

| Option | Default | Effect |
|---|---|---|
| `none_passthrough` | `False` | `None`, `""` and undefined values are returned unchanged instead of raising. |
| `coerce` | `False` | A `str` is converted to the namespace type before the call (`"2026-01-05"` → `date`). |
| `regex_timeout` | `1.0` | Seconds per regex call, with the `[regex]` extra. |
| `locale` | `None` | Default locale of `babel.*` (falls back to `en_US`). |
| `registry` | `Registry.default()` | The members to install (see [Registries](registry.md)). |

The first four are the fields of the frozen [`Options`](../reference/api.md#options) dataclass.
[Strict values and conversion](conversion.md) shows `none_passthrough` and `coerce` at work.

## Install into an existing environment

`install(env, registry=None, *, options=None, **options)` is what the extension calls. It
registers every filter, test and global and returns the registry. It is plumbing: projects that
use jinja-types (templify included) add `TypesExtension` to their environment instead, and
`install` is kept for jinja-types' own tests.

`install` raises `BuiltinClashError`, before changing anything, if a plain-name helper (`fmt`,
`to_int`, …) is already a filter, test or global of a different function in `env`.
