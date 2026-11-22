# PHASES.md: jinja-types build plan

Work top to bottom. Each phase ends with a green run of
`uv run ruff check --fix && uv run ruff format && uv run mypy && uv run pytest`
and one commit, or more. Tick the boxes as you go. Do not start a phase before the previous one is complete.

---

## Phase 0: Scaffold

- [x] `uv init --lib jinja-types` with `src/jinja_types/`, `py.typed`, Python `>=3.12`
- [x] Dependencies: `jinja2>=3.1`. Dev: `pytest`, `pytest-cov`, `mypy`, `ruff`
- [x] Extras declared, empty for now: `regex = ["regex"]`, `babel = ["babel"]`
- [x] ruff config (line length 100, rules `E F I UP B SIM RUF ANN`), mypy `strict = true`
- [x] Console script `jinja-types = "jinja_types.cli:main"` (stub)
- [x] CI workflow: lint, mypy, tests on 3.12 and 3.13
- [x] README with a one-paragraph pitch and the qualified-name rule

**Done when:** `uv run pytest` runs (0 tests) and mypy and ruff are clean.

---

## Phase 1: Core registry

The heart of the package. Build it against a tiny **demo collection** in the tests, not real types.

- [x] `core/errors.py`: `JinjaTypesError(TemplateRuntimeError)` with `filter_name`, `value_type`, `supported`, `hint`, `__cause__`. Also `RegistryError`, `DuplicateMemberError`, `BuiltinClashError`
- [x] `core/spec.py`: `Kind` (Flag: FILTER, TEST, ATTRIBUTE, GLOBAL), `Param`, `MemberSpec` (frozen, slots)
- [x] `core/namespace.py`: `Namespace(name, type, parse=None)`. `None` namespace means plain-name helpers
- [x] `core/collection.py`: `Collection(namespace, type, parse=None)` with decorators `.filter`, `.test`, `.attribute`, `.global_`, each accepting `member=`, `examples=`. Specs are built from `typing.get_type_hints` and `inspect.signature` of **our wrapper**. A `bool` return auto-adds `TEST`. Missing annotations raise `RegistryError` at decoration time
- [x] `core/registry.py`: `Registry.include(*collections, replace=False)`, `get(name)`, `specs()`, `namespaces()`, `conflicts()`, `copy()`
  - [x] Duplicate qualified name → `DuplicateMemberError` unless `replace=True`, which is recorded in `conflicts()`
  - [x] MRO dispatch table: for `ns.member` and a value of type `T`, walk `T.__mro__` up to the namespace type and pick the most specific registered `<ns_of(cls)>.member`
- [x] `core/options.py`: frozen `Options(none_passthrough=False, coerce=False, regex_timeout=1.0, locale=None)`
- [x] `core/invoker.py`: one wrapper per spec that does passthrough → coerce → isinstance check → dispatch → call → translate exceptions into `JinjaTypesError` with a hint. Hint rules live in one table, e.g. "str given to a date namespace → suggest `to_date` / `date.fromisoformat`"
- [x] `extension.py`: `TypesExtension` (Jinja `Extension`), `TypesExtension.configure(**opts)` returning a subclass, and `install(env, registry=None, **opts)`. Install registers filters, tests and globals, and raises `BuiltinClashError` if a plain helper name is already a filter or test in that env
- [x] `core/plugins.py`: `load_plugins(registry, group="jinja_types.plugins")`, which accepts a Collection or an iterable of them
- [x] `core/catalog.py`: `CatalogEntry`, `Catalog`, `registry.catalog()`, `Catalog.to_dict()/to_json()`
- [x] Test harness: `tests/test_examples.py`, `test_catalog.py` and `test_no_mutation.py`, generic over `Registry.default()` (empty for now) plus the demo collection

**Done when:**
- Dotted filters and tests render in `ImmutableSandboxedEnvironment`.
- Dispatch picks the subclass member.
- Every conflict rule has a test.
- Errors carry hints.
- A fake entry point loads a plugin collection.
- Core coverage is ≥ 95%.

---

## Phase 2: Helpers and globals

- [x] `fmt(value, spec="")` → `format(value, spec)`. Works for numbers, Decimal and dates (`{{ d | fmt('%Y-%m-%d') }}`)
- [x] Converters: `to_str`, `to_int`, `to_float`, `to_bool` (strict accepted strings; documented), `to_decimal`, `to_fraction`, `to_date` / `to_datetime` / `to_time` (ISO by default, optional `format=` for strptime), `to_timedelta` (seconds, or `days=`/`hours=` kwargs), `to_uuid`, `to_path`
- [x] Each namespace's `parse` is wired to the matching converter, used by `coerce=True`
- [x] Globals: `decimal` (Decimal, Context, all `ROUND_*`), `re` (flags only), `today()`, `now(tz=None)`
- [x] Clash check: none of the helper names is a Jinja built-in

**Done when:** `{{ "1500.5" | to_decimal | fmt(",.2f") }}` gives `1,500.50` and `{{ "05/01/2026" | to_date(format="%d/%m/%Y") | fmt("%A") }}` gives `Monday`. Both `coerce` modes and `none_passthrough` are tested.

> **Before Phase 3:** decided 2026-11-22: wrappers are written by hand, namespace by namespace.

---

## Phase 3: `str`

- [x] All public `str` methods except `maketrans` (static; only as a helper if needed): case, align/pad, strip, split/partition, find/index/count, startswith/endswith (tuple prefixes allowed), replace, removeprefix/suffix, join (`{{ ", " | str.join(items) }}`, mirroring Python), format, format_map, translate, encode, expandtabs, zfill, splitlines, all `is*` predicates (filters + tests)
- [x] Examples for every member; parity test against the real methods
- [x] Autoescape check: output stays plain `str`, so Jinja escapes it once

**Done when:** every `str` member is in the catalog with examples, and parity, examples and mypy are all green.

---

## Phase 4: Numbers — `int`, `float`, `bool`, `decimal`, `fraction`

- [x] `int`: methods (`bit_length`, `bit_count`, `to_bytes`, `as_integer_ratio`, `is_integer`, `conjugate`), attributes (`real`, `imag`, `numerator`, `denominator`), classmethod `int.from_bytes`
- [x] `float`: `is_integer`, `as_integer_ratio`, `hex`, `conjugate`, `real`, `imag`; classmethod `float.fromhex`
- [x] `bool`: its own namespace; document that `int.*` also accepts bools
- [x] `decimal`: all 55 public members (quantize, normalize, to_integral_value, compare*, max/min, sqrt, ln, log10, exp, is_* predicates, adjusted, as_tuple, …); `rounding` takes the `decimal.ROUND_*` globals
- [x] `fraction`: `limit_denominator`, `as_integer_ratio`, `is_integer`, `numerator`, `denominator`; classmethods `fraction.from_float`, `fraction.from_decimal`

**Done when:** all number namespaces pass examples and parity, and a salaries-style example (`decimal.quantize(..., rounding=decimal.ROUND_HALF_UP) | fmt(",.2f")`) is in the README.

---

## Phase 5: Dates — `date`, `datetime`, `time`, `timedelta`

- [x] `date`: `strftime`, `isoformat`, `isocalendar`, `isoweekday`, `weekday`, `toordinal`, `timetuple`, `ctime`, `replace`; attributes `year`, `month`, `day`; classmethods `date.fromisoformat`, `date.fromordinal`, `date.fromisocalendar`, `date.fromtimestamp`
- [x] `datetime`: everything from `date` that it overrides or adds (`date`, `time`, `timetz`, `timestamp`, `astimezone`, `utcoffset`, `tzname`, `dst`, `isoformat(sep, timespec)`, `replace`); attributes `hour … microsecond`, `tzinfo`, `fold`; classmethods `datetime.strptime`, `datetime.fromisoformat`, `datetime.fromtimestamp`, `datetime.combine`
- [x] `time`: `strftime`, `isoformat`, `replace`, `utcoffset`, `tzname`, `dst`; attributes
- [x] `timedelta`: `total_seconds`; attributes `days`, `seconds`, `microseconds`
- [x] Dispatch tests: `date.strftime` / `date.replace` / `date.isoformat` on a `datetime` value call the `datetime` versions
- [x] Timezone names via `zoneinfo` in `datetime.astimezone("Asia/Damascus")` (string → `ZoneInfo`; documented)

**Done when:** dates pass examples and parity, and dispatch is proven by tests.

---

## Phase 6: Regex — `re.*`, `match.*`

- [x] `regex/engine.py`: chooses stdlib `re` or the `regex` library (extra), applies `regex_timeout`, and maps timeouts and `re.error` (with position) to `JinjaTypesError`
- [x] `re` namespace (value is the string): `search`, `match`, `fullmatch`, `findall`, `finditer`, `sub`, `subn`, `split`, `escape`. Python parameter names: `pattern`, `repl`, `count`, `maxsplit`, `flags`
- [x] `re.search` / `re.match` / `re.fullmatch` also registered as **tests** (true when a match is found)
- [x] `repl` may be a string (`\1`, `\g<name>`) or a Jinja macro receiving the Match; the macro result is converted with `str()` so autoescape works once
- [x] `match` namespace: `group`, `groups`, `groupdict`, `span`, `start`, `end`, `expand`; attributes `string`, `re`, `pos`, `endpos`, `lastindex`, `lastgroup`
- [x] `re` global exposes flags only (`I M S X A U L`, long names too)

**Done when:**
- `{{ "ABC-42" | re.search("abc-(\d+)", flags=re.I) | match.group(1) }}` gives `42`.
- `{% if "2026" is re.fullmatch("\d{4}") %}` is true.
- The macro replacement works with autoescape on and off.
- A catastrophic pattern times out under `[regex]`.

---

## Phase 7: Containers — `list`, `dict`

- [x] `list`: `index`, `count`, `copy`. **Copy-then-return** for `append`, `extend`, `insert`, `remove`, `reverse`, `sort(key=None, reverse=False)`, `clear`. `pop(index=-1)` returns the item (input untouched)
- [x] `dict`: `get`, `keys`, `values`, `items`, `copy`, `fromkeys` (classmethod style). Copy-then-return for `update`, `clear`. `pop`, `popitem` and `setdefault` return Python's value (input untouched)
- [x] `sort(key=...)` accepts a Jinja macro or an attribute name string (documented)
- [x] `test_no_mutation.py` covers every member

**Done when:** containers pass examples, parity (against copies) and no-mutation.

---

## Phase 8: `uuid`, `path`

- [x] `uuid`: attributes `hex`, `int`, `bytes`, `urn`, `version`, `variant`, `fields`, `time`, `node`. Global `uuid5(namespace, name)` only; no `uuid4()`, so renders stay repeatable (decided 2026-11-22)
- [x] `path` (PurePath only): `name`, `stem`, `suffix`, `suffixes`, `parent`, `parents`, `parts`, `anchor`, `drive`, `root`, `as_posix`, `as_uri`, `with_name`, `with_stem`, `with_suffix`, `joinpath`, `relative_to`, `is_relative_to`, `is_absolute`, `match`, `full_match` (3.13+, guarded)
- [x] Test asserting that no `path.*` member performs I/O (the allowlist is explicit)

**Done when:** both namespaces pass examples and parity, and the no-I/O test is green.

---

## Phase 9: Catalog export and CLI

- [x] `jinja-types catalog [--namespace NS] [--kind filter|test|attribute|global] [--format json|markdown]`
- [x] `jinja-types conflicts`, which prints `registry.conflicts()`
- [x] Docs generator: `scripts/gen_docs.py` writes one Markdown page per namespace from the catalog (examples included)
- [x] JSON schema for the catalog committed under `schema/catalog.schema.json`, with a test that the export validates against it

**Done when:** the CLI works on the default registry plus a fake plugin, and the generated docs are committed.

---

## Phase 10: `[babel]` extra

- [ ] `contrib/babel.py` collection, namespace `babel`: `format_decimal`, `format_currency`, `format_percent`, `format_compact_decimal`, `format_date`, `format_datetime`, `format_time`, `format_timedelta`
- [ ] Locale comes from `Options.locale`, overridable per call (`locale="ar_SY"`)
- [ ] Registered only when Babel is importable; a clear error otherwise

**Done when:** examples pass with Babel installed and are skipped without it, and the `ar_SY` / `en_US` currency examples are documented.

---

## Phase 11: templify integration and 0.1.0 release

- [ ] templify depends on `jinja-types` and calls `install(env, …)` on its sandboxed env
- [ ] templify reads `registry.catalog()` for autocomplete and validation
- [ ] Plugin author guide (`docs/plugins.md`) with a full example collection and an entry point
- [ ] CHANGELOG, version `0.1.0`, publish to PyPI (trusted publishing)

**Done when:** templify renders a real template (salary letter / fee table) using only qualified jinja-types filters.

---

## Later (not v1)

- arapy plugin (Arabic: amount in words, digits, dates), shipped from arapy through the `jinja_types.plugins` entry point
- `re.compile` global and `pattern.*` members
- Extra families (base64, hashing, JSON, URL parsing) as separate collections
