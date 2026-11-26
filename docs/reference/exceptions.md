# Exceptions

```text
jinja2.TemplateRuntimeError
└── JinjaTypesError          raised while rendering
Exception
└── RegistryError            raised while building a registry or installing it
    ├── DuplicateMemberError
    └── BuiltinClashError
```

## JinjaTypesError

Every failure of a jinja-types filter, test or global while rendering raises `JinjaTypesError`,
a subclass of `jinja2.TemplateRuntimeError`. The message is
`<member>: <what went wrong>. Hint: <how to fix it>.`

| Attribute | Value |
|---|---|
| `filter_name` | The member's name (`date.strftime`). |
| `value_type` | The piped value's type name, when known. |
| `supported` | Type names the namespace accepts (`('date', 'datetime')`). |
| `hint` | The fix, or `None`. |
| `original` | The underlying exception, or `None`. |

```python
from jinja_types import JinjaTypesError

try:
    env.from_string('{{ "2026-01-05" | date.strftime("%d") }}').render()
except JinjaTypesError as error:
    error.filter_name  # 'date.strftime'
    error.value_type   # 'str'
    error.supported    # ('date', 'datetime')
    error.hint         # "convert first with '| to_date' or '| date.fromisoformat'"
```

| Cause | Hint |
|---|---|
| `None`, `""` or undefined input | `pass a value, or install with none_passthrough=True` |
| Wrong type, or a string `coerce=True` cannot parse | `convert first with '| to_…'` |
| `TypeError` from the call | `check the arguments: <signature>` |
| Regex timeout (`[regex]` extra) | `simplify the pattern, or install with a larger regex_timeout` |
| Missing optional extra | `install 'jinja-types[<extra>]'` |

## RegistryError

A collection or registry was set up incorrectly, for example a namespace name bound to two
different types.

## DuplicateMemberError

The same qualified name was registered twice without `replace=True`.

## BuiltinClashError

A plain-name helper has the same name as an existing Jinja filter, test or global in the
environment being installed into.
