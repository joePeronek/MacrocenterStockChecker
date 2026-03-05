from macrocenter_stock_checker import __version__
from macrocenter_stock_checker.cli import main


def test_version_is_defined() -> None:
    assert __version__


def test_cli_runs_without_arguments(capsys) -> None:
    exit_code = main([])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "foundation is set up" in captured.out
