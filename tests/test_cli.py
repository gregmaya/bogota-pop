"""Tests for the ``bogota-pop`` command-line interface."""

import subprocess
import sys
from importlib.metadata import version

import pytest
from typer.testing import CliRunner

from bogota_pop.cli import app

runner = CliRunner()

STAGES = ["ingest", "model", "validate", "publish"]


def test_help_lists_every_stage() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for stage in STAGES:
        assert stage in result.output


def test_no_arguments_shows_help() -> None:
    result = runner.invoke(app, [])
    assert "Usage" in result.output


def test_version_matches_package_metadata() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == f"bogota-pop {version('bogota-pop')}"


@pytest.mark.parametrize("stage", STAGES)
def test_stage_stub_runs(stage: str) -> None:
    result = runner.invoke(app, [stage])
    assert result.exit_code == 0
    assert "not implemented yet" in result.output


def test_unknown_command_fails() -> None:
    result = runner.invoke(app, ["nope"])
    assert result.exit_code == 2


def test_help_does_not_import_heavy_libraries() -> None:
    """ADR-0009: keep ``bogota-pop --help`` fast by importing heavy libraries lazily."""
    heavy = ["geopandas", "duckdb", "tobler", "pyogrio", "h3"]
    code = (
        "import sys\n"
        "from bogota_pop.cli import app\n"
        "try:\n"
        "    app(['--help'])\n"
        "except SystemExit:\n"
        "    pass\n"
        f"print('LOADED=' + ','.join(m for m in {heavy!r} if m in sys.modules))\n"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    ).stdout
    [line] = [ln for ln in out.splitlines() if ln.startswith("LOADED=")]
    loaded = line.removeprefix("LOADED=")
    assert loaded == "", f"--help imported heavy libraries: {loaded}"
