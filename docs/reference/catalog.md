# Catalog and CLI

## The `jinja-types` command

```text
jinja-types catalog [--namespace NAME] [--kind {filter,test,attribute,global}]
                    [--format {json,markdown}] [--plugins]
jinja-types conflicts [--plugins]
```

- `catalog` prints the catalog, as JSON (default) or Markdown. `--namespace helpers` selects the
  plain-name helpers. It exits with status 1 when no member matches.
- `conflicts` prints one tab-separated line per conflict: name, resolution, detail.
- `--plugins` also loads the `jinja_types.plugins` entry points.

## JSON format

`Catalog.to_json()` and `jinja-types catalog` write one object with an `entries` array. The
format is described by the JSON Schema in
[`schema/catalog.schema.json`](https://github.com/aaltatan/jinja-types/blob/main/schema/catalog.schema.json).

```json
{
  "entries": [
    {
      "name": "str.endswith",
      "kinds": ["filter", "test"],
      "namespace": "str",
      "input_type": "str",
      "params": [
        {"name": "suffix", "kind": "positional_only", "annotation": "str | tuple[str, ...]", "default": null},
        {"name": "start", "kind": "positional_only", "annotation": "int | None", "default": "None"},
        {"name": "end", "kind": "positional_only", "annotation": "int | None", "default": "None"}
      ],
      "returns": "bool",
      "doc": "Return True if the string ends with `suffix` (or any suffix in a tuple).",
      "examples": [["{{ 'report.pdf' | str.endswith('.pdf') }}", {}, "True"]],
      "source": "jinja_types",
      "replaced": false,
      "constant": false,
      "classmethod": false
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `name` | Qualified name (`str.endswith`) or plain name (`fmt`). |
| `kinds` | Any of `filter`, `test`, `attribute`, `global`. |
| `namespace` | Namespace name, or `null` for plain-name helpers. |
| `input_type` | Type of the piped value, or `null` for globals. |
| `params` | Parameters after the piped value: `name`, `kind`, `annotation`, `default` (`repr()` or `null` when required). |
| `returns` | Return annotation. |
| `doc` | The docstring. |
| `examples` | `[template, context, expected_output]` triples; non-JSON context values are written as `repr()`. |
| `source` | `jinja_types`, or the plugin's entry-point name. |
| `replaced` | The member overrides an earlier one (`replace=True`). |
| `constant` | A global whose value is an object rather than a function. |
| `classmethod` | A parsing filter: the piped value is not checked against the namespace type. |
