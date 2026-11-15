"""Tests for the ``bogota-pop`` command-line interface."""

import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import pytest
import yaml
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


@pytest.mark.parametrize("stage", ["model", "validate", "publish"])
def test_stage_stub_runs(stage: str) -> None:
    result = runner.invoke(app, [stage])
    assert result.exit_code == 0
    assert "not implemented yet" in result.output


def _sources_yaml(tmp_path: Path, url: str | None, sha: str | None = None) -> Path:
    path = tmp_path / "sources.yaml"
    entry = {"title": "Prueba", "download_url": url, "vigencia": "2026", "sha256": sha}
    path.write_text(yaml.safe_dump({"sources": {"prueba": entry}}))
    return path


def _ingest(tmp_path: Path, sources: Path, *args: str):
    return runner.invoke(
        app,
        [
            "ingest",
            *args,
            "--sources-yaml",
            str(sources),
            "--data-dir",
            str(tmp_path / "data"),
            "--manifest-json",
            str(tmp_path / "manifest.json"),
        ],
    )


def test_ingest_with_no_urls_does_nothing(tmp_path: Path) -> None:
    result = _ingest(tmp_path, _sources_yaml(tmp_path, None))
    assert result.exit_code == 0
    assert "no source has a download_url" in result.output


def test_ingest_unknown_source_fails(tmp_path: Path) -> None:
    result = _ingest(tmp_path, _sources_yaml(tmp_path, None), "no_existe")
    assert result.exit_code == 1
    assert "not in sources.yaml" in result.output


def test_ingest_checksum_mismatch_exits_1(tmp_path: Path) -> None:
    import geopandas as gpd
    from shapely.geometry import Point

    src = tmp_path / "capa.gpkg"
    gpd.GeoDataFrame({"a": [1]}, geometry=[Point(-74.08, 4.6)], crs=4686).to_file(src)
    result = _ingest(tmp_path, _sources_yaml(tmp_path, src.as_uri(), "0" * 64))
    assert result.exit_code == 1
    assert "not the pinned one" in result.output


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
