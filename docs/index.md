# jinja-types

`jinja-types` is a Jinja2 extension that exposes the methods and attributes of everyday Python
types as Jinja filters and tests: `str`, `int`, `float`, `bool`, `Decimal`, `Fraction`, `date`,
`datetime`, `time`, `timedelta`, `list`, `dict`, `UUID`, `PurePath`, plus the `re` module,
compiled patterns and matches. Arabic text, numbers and dates come from
[arapy](https://pypi.org/project/arapy/) under `ar.*`, and locale formatting from Babel under
`babel.*`.

```python
from decimal import Decimal

from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import TypesExtension

env = ImmutableSandboxedEnvironment(extensions=[TypesExtension])

template = env.from_string(
    '{{ salary | decimal.quantize(decimal.Decimal("0.01"), rounding=decimal.ROUND_HALF_UP)'
    ' | fmt(",.2f") }}'
)

template.render(salary=Decimal("1500.005"))  # '1,500.01'
```

## Why jinja-types

- **Names identical to Python.** `str.zfill`, `decimal.quantize`, `date.strftime`, `re.sub`,
  `match.group`: the member name, parameter names and order are Python's own.
- **Qualified names only.** Every type member lives under its namespace, so nothing clashes
  with Jinja's built-in `count`, `format`, `join` or `replace`.
- **Sandbox-safe.** Everything works in `ImmutableSandboxedEnvironment`. Nothing touches the
  disk, the network or processes, and mutating methods (`list.sort`, `dict.update`) return
  new objects.
- **Strict, with one error type.** `None`, `""` and wrong types raise `JinjaTypesError` with a
  hint that names the fix. Leniency (`none_passthrough`, `coerce`) is opt-in.
- **A registry and a typed catalog.** Add your own namespaces as collections or installable
  plugins; every member is described (signature, kinds, examples) for docs and autocomplete.

```jinja
{{ code | str.zfill(5) }}                         {# '42' → 00042 #}
{{ invoice_date | date.strftime("%d/%m/%Y") }}    {# 05/01/2026 #}
{% if code is str.isdigit %}…{% endif %}
{{ code | re.search("abc-(\\d+)", flags=re.I) | match.group(1) }}
```

## Where to next

- [Installation](install.md): the package and its extras.
- [User guide](guide/index.md): how names, kinds and dispatch work, then one page per topic.
- [Types and namespaces](guide/types/index.md): every member with its signature and examples.
- [Recipes](recipes.md): money, dates, cleanup and Arabic output.
- [Reference](reference/index.md): the Python API, the catalog format and the errors.
