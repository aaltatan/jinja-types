# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-11-22

First release.

### Added

- Qualified filters and tests for the members of `str`, `int`, `bool`, `float`, `Decimal`,
  `Fraction`, `date`, `datetime`, `time`, `timedelta`, `list`, `dict`, `UUID` and `PurePath`,
  with Python's names and parameters (`str.zfill`, `decimal.quantize`, `date.strftime`, ...).
  Predicates are also tests; classmethods are parsing filters; mutating `list` / `dict` methods
  return copies.
- Regex: the `re` namespace (module functions, the string is piped in), `match` for match
  objects, and `pattern` for compiled patterns from the `re.compile` global. Macros work as
  `sub` replacements. The `[regex]` extra adds timeouts (`regex_timeout`).
- Helpers with plain names: `fmt` and the `to_*` converters; globals `decimal`, `re` (flags and
  `compile`), `today()`, `now()` and `uuid5()`.
- The `ar` namespace, backed by [arapy](https://pypi.org/project/arapy/): Arabic words for
  numbers and money, digits, normalization, sorting, ordinals and dates. The `[hijri]` and
  `[shape]` extras add Hijri dates and shaping.
- The `[babel]` extra: `babel.*` locale-aware numbers, currencies and dates.
- `TypesExtension` (and `TypesExtension.configure(...)`) for any Jinja environment, built for
  `ImmutableSandboxedEnvironment`. Options: `none_passthrough`, `coerce`, `regex_timeout`,
  `locale`.
- `JinjaTypesError` with the member name, the value's type, the supported types and a hint.
- A registry with conflict rules, plugins through the `jinja_types.plugins` entry point, and a
  catalog exported as JSON (with a schema) or Markdown by the `jinja-types` command.
- Generated reference docs in `docs/` and a plugin author guide (`docs/plugins.md`).

[0.1.0]: https://github.com/aaltatan/jinja-types/releases/tag/v0.1.0
