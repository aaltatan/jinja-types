# Regular expressions

Three namespaces cover regular expressions:

- [`re`](types/re.md): the module functions. The piped value is the string being searched.
- [`pattern`](types/pattern.md): members of a compiled pattern. The pattern is the piped value.
- [`match`](types/match.md): members of a match object (`group`, `groups`, `span`, …).

## Module functions

Parameter names are Python's, so flags are passed as `flags=`:

```jinja
{{ code | re.search("abc-(\\d+)", flags=re.I) | match.group(1) }}   {# ABC-123 → 123 #}
{% if code is re.fullmatch("\\d{4}") %}four digits{% endif %}
```

`re.search`, `re.match` and `re.fullmatch` are also tests: true when there is a match.

!!! tip "Backslashes"
    Jinja string literals process backslash escapes, so write `\\d` for the regex `\d`.

The flags live on the `re` global: `re.I`, `re.M`, `re.S`, `re.X`, `re.A`, …

## Compiled patterns

`re.compile(pattern, flags=0)` on the `re` global returns a cached compiled pattern. Its members
are the `pattern` namespace, with the pattern piped in, as in Python:

```jinja
{% set word = re.compile("\\w+", re.I) %}
{{ word | pattern.findall(text) | join(", ") }}     {# hello, big, world #}
{% if word is pattern.fullmatch(name) %}one word{% endif %}
```

## Macro replacements

`re.sub`, `re.subn`, `pattern.sub` and `pattern.subn` accept a string replacement or a **Jinja
macro** that takes the match. Under autoescape, the macro output is kept as markup and the rest
of the string is escaped once:

```jinja
{% macro up(m) %}<{{ m.group(0) | str.upper }}>{% endmacro %}
{{ text | re.sub("\\w+", up) }}
```

With `text = "a & b"` and autoescape on, this renders `<A> &amp; <B>`.

## The `regex` engine and timeouts

The default engine is the standard library `re`. With the `[regex]` extra installed, the
[`regex`](https://pypi.org/project/regex/) library is used instead, and every call is limited by
the `regex_timeout` option (seconds, default `1.0`):

```python
env = ImmutableSandboxedEnvironment(
    extensions=[TypesExtension.configure(regex_timeout=0.5)],
)
```

A timeout raises `JinjaTypesError` with the hint
`simplify the pattern, or install with a larger regex_timeout`.
