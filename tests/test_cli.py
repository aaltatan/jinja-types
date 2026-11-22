"""Phase 9: the `jinja-types` command."""

import json

import pytest
from test_core import fake_entry_points

from jinja_types.cli import main
from jinja_types.core import plugins


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    code = main(list(argv))
    out, err = capsys.readouterr()

    return code, out, err


def test_catalog_json(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = run(capsys, "catalog")
    names = {entry["name"] for entry in json.loads(out)["entries"]}

    assert code == 0
    assert {"str.zfill", "re.search", "to_date", "uuid5"} <= names


def test_catalog_filters(capsys: pytest.CaptureFixture[str]) -> None:
    _, out, _ = run(capsys, "catalog", "--namespace", "re", "--kind", "test")

    assert [entry["name"] for entry in json.loads(out)["entries"]] == [
        "re.fullmatch",
        "re.match",
        "re.search",
    ]

    _, out, _ = run(capsys, "catalog", "--namespace", "helpers", "--kind", "global")

    assert {entry["namespace"] for entry in json.loads(out)["entries"]} == {None}


def test_catalog_markdown(capsys: pytest.CaptureFixture[str]) -> None:
    _, out, _ = run(capsys, "catalog", "--namespace", "str", "--format", "markdown")

    assert out.startswith("# `str`\n\n## `str.capitalize`\n")
    assert "`str.zfill(value: str, width: int, /) -> str`" in out


def test_no_match(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys, "catalog", "--namespace", "nope")

    assert (code, out) == (1, "")
    assert "no members match" in err


def test_conflicts(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = run(capsys, "conflicts")

    assert code == 0
    assert "datetime.replace\tdispatch\toverrides date.replace for datetime values\n" in out


def test_plugins_are_loaded_only_when_asked(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(plugins, "entry_points", fake_entry_points(("acme", "demo:collections")))

    _, out, _ = run(capsys, "catalog", "--namespace", "helpers", "--plugins")
    sources = {entry["name"]: entry["source"] for entry in json.loads(out)["entries"]}

    assert sources["shout"] == "acme"
    assert sources["to_int"] == "jinja_types"

    _, out, _ = run(
        capsys, "catalog", "--namespace", "helpers", "--plugins", "--format", "markdown"
    )

    assert "## `shout`\n\n`shout(value: str, /) -> str`\n\n*filter, from acme*" in out

    _, out, _ = run(capsys, "catalog", "--namespace", "helpers")

    assert "shout" not in out


def test_a_command_is_required(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as info:
        main([])

    assert info.value.code == 2
    assert "required" in capsys.readouterr().err
