"""Every spec is documented, has examples and is fully annotated."""

import json

import pytest
from demo import demo_registry

from jinja_types.core import MemberSpec

SPECS = demo_registry().specs()


@pytest.mark.parametrize("spec", SPECS, ids=lambda spec: spec.name)
def test_spec_is_complete(spec: MemberSpec) -> None:
    assert spec.doc, f"{spec.name} has no docstring"
    assert spec.examples, f"{spec.name} has no examples"
    assert spec.returns
    assert all(param.annotation for param in spec.params)


def test_catalog_json_round_trip() -> None:
    catalog = demo_registry().catalog()
    data = json.loads(catalog.to_json())
    entries = {entry["name"]: entry for entry in data["entries"]}

    assert len(catalog) == len(SPECS) == len(entries)
    assert [entry.name for entry in catalog] == [spec.name for spec in SPECS]
    assert entries["is_even"]["kinds"] == ["filter", "test"]
    assert entries["date.year"]["kinds"] == ["attribute"]
    assert entries["date.strftime"]["input_type"] == "date"
    assert entries["date.strftime"]["params"] == [
        {"name": "format", "kind": "positional_or_keyword", "annotation": "str", "default": None}
    ]
    assert entries["answer"]["input_type"] is None
    assert entries["date.year"]["examples"][0][1] == {"x": "datetime.date(2026, 11, 22)"}
