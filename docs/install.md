# Installation

jinja-types needs Python 3.12 or newer. Its runtime dependencies are `jinja2>=3.1` and
`arapy>=0.1.0`.

=== "uv"

    ```bash
    uv add jinja-types
    ```

=== "pip"

    ```bash
    pip install jinja-types
    ```

## Extras

| Extra | Adds | Enables |
|---|---|---|
| `regex` | the `regex` library | `re.*` / `pattern.*` run on `regex`, limited by `regex_timeout` |
| `babel` | Babel | the `babel.*` namespace (locale numbers, money, dates) |
| `hijri` | `arapy[hijri]` | `ar.to_hijri` |
| `shape` | `arapy[shape]` | `ar.shape` and `ar.reshape_only` |

```bash
uv add "jinja-types[regex,babel]"
```

Calling a member whose extra is missing raises `JinjaTypesError` with a hint such as
`install 'jinja-types[hijri]'`.

!!! note "Timezone names on Windows"
    `datetime.astimezone("Asia/Damascus")` resolves IANA names with `zoneinfo`. Windows ships no
    timezone database, so install the `tzdata` package there.

## Check the install

The package installs a `jinja-types` command that prints the catalog:

```bash
jinja-types catalog --namespace str --format markdown
```
