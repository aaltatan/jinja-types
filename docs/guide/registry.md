# Registries and the catalog

## The registry

A `Registry` holds every member, keyed by qualified name. `Registry.default()` has all the
built-in collections; pass your own to the extension to add or replace members:

```python
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import Registry, TypesExtension

registry = Registry.default()
registry.include(my_collection)              # DuplicateMemberError on a clash
registry.include(other, replace=True)        # explicit override
registry.load_plugins()                      # entry points in "jinja_types.plugins"

env = ImmutableSandboxedEnvironment(
    extensions=[TypesExtension.configure(registry=registry, none_passthrough=True)],
)
```

`include` changes nothing if any of the collections conflicts. `Registry.default(plugins=True)`
is the same as calling `load_plugins()`. Plugins are loaded only on request, so a render never
changes because a package happened to be installed.

A collection is a set of members for one namespace, filled with decorators.
[Writing a plugin](plugins.md) builds one step by step.

## Conflict rules

| Situation | Result |
|---|---|
| Same qualified name twice | `DuplicateMemberError`, unless `replace=True` |
| Namespace name bound to a different type | `RegistryError` |
| Plain-name helper equals an existing Jinja filter, test or global | `BuiltinClashError` when installing |
| Same member on a parent and a child namespace (`date.ctime` / `datetime.ctime`) | Both kept; dispatch picks the most specific |

`registry.conflicts()` returns every decision as a `Conflict(name, resolution, detail)`, with
`resolution` either `"replaced"` or `"dispatch"`:

```python
Registry.default().conflicts()[0]
# Conflict(name='datetime.ctime', resolution='dispatch',
#          detail='overrides date.ctime for datetime values')
```

## The catalog

`registry.catalog()` returns a typed `Catalog` of `CatalogEntry` objects: name, kinds,
namespace, input type, parameters, return type, docstring, examples and source. Tooling uses it
for autocomplete, and the [Types and namespaces](types/index.md) pages are generated from it.

```python
catalog = Registry.default().catalog()

tests = catalog.select(namespace="str", kind="test")
[entry.name for entry in tests][:3]   # ['str.endswith', 'str.isalnum', 'str.isalpha']

catalog.namespaces()                  # ['ar', 'babel', 'date', ..., 'helpers', ...]
print(tests.to_json())
print(tests.to_markdown())
```

The same export is available from the command line. See
[Catalog and CLI](../reference/catalog.md) for the JSON format.

```bash
jinja-types catalog --namespace str --format markdown
jinja-types catalog --kind test
jinja-types conflicts --plugins
```
