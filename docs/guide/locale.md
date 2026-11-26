# Locales and Arabic

## Babel: locale numbers, money and dates

With the `[babel]` extra, the [`babel`](types/babel.md) namespace formats numbers, money and dates
for a locale. The locale is the `locale=` argument, else the `locale` option of
`TypesExtension.configure(...)`, else `en_US`:

```python
env = ImmutableSandboxedEnvironment(
    extensions=[TypesExtension.configure(locale="ar_SY")],
)
```

```jinja
{{ salary | babel.format_currency("USD") }}                                          {# $1,234.50 (en_US) #}
{{ salary | babel.format_currency("SYP", locale="ar_SY", currency_digits=false) }}  {# ‏1,234.50 ل.س.‏ #}
{{ salary | babel.format_decimal(locale="ar_SY", numbering_system="default") }}     {# 1٬234٫5 #}
```

`SYP` has no minor unit in CLDR, so `currency_digits=false` is needed to show piastres.
`numbering_system="default"` uses the locale's own separators (`٬` and `٫`). Babel keeps Latin
digits either way; Arabic-Indic digits come from `ar.*`.

## arapy: Arabic text, numbers and dates

Arabic filters come from [arapy](https://pypi.org/project/arapy/), a runtime dependency, under
the [`ar`](types/ar.md) namespace: number words, ordinals, money, dates, digits, normalization
and sorting.

arapy ships no currencies. Define one in Python and pass it to the template:

```python
from arapy import Currency, Gender, Noun

qirsh = Noun.create("قرش", "قرشان", "قروش", gender=Gender.MASCULINE)
syp = Currency.create(
    code="SYP",
    singular="ليرة سورية",
    dual="ليرتان سوريتان",
    plural="ليرات سورية",
    gender=Gender.FEMININE,
    subunit=qirsh,
    symbol="ل.س",
)
```

```jinja
{{ salary | ar.to_words(syp) }}       {# ألف وخمسمئة ليرة سورية #}
{{ salary | ar.format_money(syp) }}   {# ١٬٥٠٠ ل.س #}
{{ day | ar.format_date("%A %d %B %Y", digits="arabic") }}
```

Two members need extras:

- `ar.to_hijri` needs `jinja-types[hijri]`.
- `ar.shape` and `ar.reshape_only` need `jinja-types[shape]`.

Without them, the call raises `JinjaTypesError` with the hint `install 'jinja-types[hijri]'`
(or `[shape]`). arapy's own errors also surface as `JinjaTypesError`.
