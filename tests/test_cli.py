from jinja_types.cli import main


def test_cli_stub_runs() -> None:
    assert main([]) == 0
