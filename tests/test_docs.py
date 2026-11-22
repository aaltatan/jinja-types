"""Phase 9: the catalog schema, Markdown signatures and the generated docs."""

import json
import runpy
import sys
from pathlib import Path

import jsonschema
import pytest
from demo import demo_registry

from jinja_types import Registry
from jinja_types.core.catalog import signature

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "schema" / "catalog.schema.json").read_text(encoding="utf-8"))
HAND_WRITTEN = {"plugins.md"}  # not generated from the catalog


def test_catalog_export_matches_the_schema() -> None:
    data = json.loads(demo_registry().catalog().to_json())

    jsonschema.validate(data, SCHEMA)


def test_schema_rejects_a_broken_entry() -> None:
    data = json.loads(Registry.default().catalog().select(namespace="int").to_json())

    data["entries"][0]["kinds"] = ["macro"]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(data, SCHEMA)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        (
            "list.sort",
            "list.sort(value: list[Any], /, *, key: str | Callable[[Any], object] | None",
        ),
        ("path.joinpath", "path.joinpath(value: PurePath, /, *pathsegments: str | PurePath)"),
        ("dict.update", "dict.update(value: dict[Any, Any], other: "),
        ("now", "now(tz: tzinfo | None = None) -> datetime"),
    ],
)
def test_signatures(name: str, expected: str) -> None:
    entry = next(e for e in Registry.default().catalog() if e.name == name)

    assert signature(entry).startswith(expected)


def test_var_keyword_signature() -> None:
    entry = next(e for e in Registry.default().catalog() if e.name == "dict.update")

    assert signature(entry).endswith(", /, **kwargs: object) -> dict[Any, Any]")


@pytest.mark.skipif(sys.version_info >= (3, 13), reason="the docs are generated on Python 3.12")
def test_generated_docs_are_up_to_date() -> None:
    pages = runpy.run_path(str(ROOT / "scripts" / "gen_docs.py"))["pages"]
    docs = ROOT / "docs"

    expected = pages(Registry.default().catalog())

    written = sorted(path.name for path in docs.glob("*.md") if path.name not in HAND_WRITTEN)

    assert written == sorted(expected)

    for name, text in expected.items():
        assert (docs / name).read_text(encoding="utf-8") == text, (
            f"docs/{name} is stale: run `uv run python scripts/gen_docs.py`"
        )


@pytest.mark.skipif(sys.version_info >= (3, 13), reason="the docs are generated on Python 3.12")
def test_readme_reference_is_up_to_date() -> None:
    readme = runpy.run_path(str(ROOT / "scripts" / "gen_docs.py"))["readme"]
    text = (ROOT / "README.md").read_text(encoding="utf-8")

    assert readme(text, Registry.default().catalog()) == text, (
        "the README reference is stale: run `uv run python scripts/gen_docs.py`"
    )
