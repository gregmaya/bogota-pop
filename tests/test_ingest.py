"""Tests for the shared ingest machinery (ADR-0012).

No network: sources point at ``file://`` URLs in a temp folder, which urllib
downloads through the same code path as https.
"""

import hashlib
import json
import zipfile
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point

from bogota_pop.ingest import convert, manifest
from bogota_pop.ingest.core import ingest_source
from bogota_pop.ingest.errors import (
    ChecksumMismatch,
    IngestError,
    MissingCRS,
    NoDownloadUrl,
    UnknownSource,
    UnpinnedSource,
)
from bogota_pop.ingest.sources import Source, load_sources

# Plaza de Bolívar and a point in Suba, in MAGNA-SIRGAS geographic (EPSG:4686).
POINTS = [Point(-74.0761, 4.5981), Point(-74.0836, 4.7411)]


@pytest.fixture(autouse=True)
def no_retry_wait(monkeypatch: pytest.MonkeyPatch) -> None:
    """Failed downloads retry with a pause; skip the pause in tests."""
    monkeypatch.setattr("bogota_pop.ingest.download.time.sleep", lambda _: None)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def gpkg(tmp_path: Path) -> Path:
    """A two-point GeoPackage in EPSG:4686, standing in for a published layer."""
    src = tmp_path / "portal" / "manzanas.gpkg"
    src.parent.mkdir()
    gdf = gpd.GeoDataFrame({"CODMANPRE": ["001", "002"]}, geometry=POINTS, crs=4686)
    gdf.to_file(src, driver="GPKG")
    return src


def make_source(path: Path, sha: str | None = None, **kw) -> Source:
    return Source(
        id=kw.get("id", "fuente_prueba"),
        title="Fuente de prueba",
        download_url=kw.get("download_url", path.as_uri()),
        vigencia=kw.get("vigencia", "2026"),
        sha256=sha,
    )


def run(source: Source, tmp_path: Path, **kw):
    return ingest_source(
        source, data_dir=tmp_path / "data", manifest_path=tmp_path / "manifest.json", **kw
    )


# ── sources.yaml ──────────────────────────────────────────────────────────────


def test_load_sources_reads_the_real_config() -> None:
    sources = load_sources()
    assert "dane_mgn_cnpv2018_manzana" in sources
    assert sources["dane_mgn_cnpv2018_manzana"].vigencia == "2018"


def test_unknown_source_id_fails() -> None:
    from bogota_pop.ingest.sources import get_source

    with pytest.raises(UnknownSource):
        get_source("no_existe", load_sources())


def test_source_without_url_fails(tmp_path: Path, gpkg: Path) -> None:
    with pytest.raises(NoDownloadUrl):
        run(make_source(gpkg, download_url=None), tmp_path)


def test_source_without_vigencia_fails(tmp_path: Path, gpkg: Path) -> None:
    with pytest.raises(IngestError, match="vigencia"):
        run(make_source(gpkg, vigencia=None), tmp_path)


# ── checksum rules (ADR-0012) ─────────────────────────────────────────────────


def test_pinned_and_matching_writes_raw_and_interim(tmp_path: Path, gpkg: Path) -> None:
    entry = run(make_source(gpkg, sha256(gpkg)), tmp_path)
    raw = tmp_path / "data/raw/fuente_prueba/2026/manzanas.gpkg"
    interim = tmp_path / "data/interim/fuente_prueba/2026.parquet"
    assert raw.exists() and interim.exists()
    assert entry["pinned"] is True
    assert entry["sha256"] == sha256(gpkg)


def test_pinned_and_different_stops_and_sets_file_aside(tmp_path: Path, gpkg: Path) -> None:
    with pytest.raises(ChecksumMismatch) as err:
        run(make_source(gpkg, "0" * 64), tmp_path)
    assert sha256(gpkg) in str(err.value)
    assert not (tmp_path / "data/raw/fuente_prueba/2026/manzanas.gpkg").exists()
    assert (tmp_path / "data/raw/_rejected/fuente_prueba/2026/manzanas.gpkg").exists()
    assert not (tmp_path / "data/interim/fuente_prueba/2026.parquet").exists()
    assert not (tmp_path / "manifest.json").exists()


def test_unpinned_warns_and_continues(
    tmp_path: Path, gpkg: Path, caplog: pytest.LogCaptureFixture
) -> None:
    entry = run(make_source(gpkg), tmp_path)
    assert entry["pinned"] is False
    assert sha256(gpkg) in caplog.text
    assert "not pinned" in caplog.text


def test_unpinned_with_strict_fails_before_downloading(tmp_path: Path, gpkg: Path) -> None:
    with pytest.raises(UnpinnedSource):
        run(make_source(gpkg), tmp_path, strict=True)
    assert not (tmp_path / "data/raw").exists()


def test_cached_copy_skips_download(tmp_path: Path, gpkg: Path) -> None:
    source = make_source(gpkg, sha256(gpkg))
    run(source, tmp_path)
    gpkg.unlink()  # the "portal" is gone; only the cached copy can work
    entry = run(source, tmp_path)
    assert entry["sha256"] == source.sha256


def test_force_downloads_again(tmp_path: Path, gpkg: Path) -> None:
    source = make_source(gpkg, sha256(gpkg))
    run(source, tmp_path)
    gpkg.unlink()
    with pytest.raises(IngestError):
        run(source, tmp_path, force=True)


def test_no_part_file_left_after_a_download(tmp_path: Path, gpkg: Path) -> None:
    run(make_source(gpkg, sha256(gpkg)), tmp_path)
    assert not list((tmp_path / "data").rglob("*.part"))


# ── manifest.json ─────────────────────────────────────────────────────────────


def test_manifest_records_what_happened(tmp_path: Path, gpkg: Path) -> None:
    run(make_source(gpkg, sha256(gpkg)), tmp_path)
    data = json.loads((tmp_path / "manifest.json").read_text())
    entry = data["sources"]["fuente_prueba"]
    assert data["schema_version"] == 1
    assert entry["url"] == gpkg.as_uri()
    assert entry["vigencia"] == "2026"
    assert entry["sha256"] == sha256(gpkg)
    assert entry["size_bytes"] == gpkg.stat().st_size
    assert entry["rows"] == 2
    assert entry["crs_in"] == "EPSG:4686"
    assert entry["crs_out"] == "EPSG:9377"
    assert entry["downloaded_at"].endswith("Z")


def test_manifest_untouched_when_nothing_changed(tmp_path: Path, gpkg: Path) -> None:
    source = make_source(gpkg, sha256(gpkg))
    run(source, tmp_path)
    before = (tmp_path / "manifest.json").read_text()
    run(source, tmp_path, force=True)
    assert (tmp_path / "manifest.json").read_text() == before


def test_manifest_keeps_other_sources(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    manifest.record(path, "a", {"sha256": "1"})
    manifest.record(path, "b", {"sha256": "2"})
    assert set(manifest.read(path)["sources"]) == {"a", "b"}


# ── conversion to GeoParquet ──────────────────────────────────────────────────


def test_reprojects_to_magna_sirgas_origen_nacional(tmp_path: Path, gpkg: Path) -> None:
    run(make_source(gpkg, sha256(gpkg)), tmp_path)
    gdf = gpd.read_parquet(tmp_path / "data/interim/fuente_prueba/2026.parquet")
    assert gdf.crs.to_epsg() == 9377
    # Origen Nacional: false easting 5,000,000 at 73°W, false northing 2,000,000 at 4°N.
    # Plaza de Bolívar sits ~120 km west and ~66 km north of that origin.
    x, y = gdf.geometry.iloc[0].x, gdf.geometry.iloc[0].y
    assert 4_870_000 < x < 4_890_000
    assert 2_055_000 < y < 2_075_000


def test_keeps_source_field_names(tmp_path: Path, gpkg: Path) -> None:
    run(make_source(gpkg, sha256(gpkg)), tmp_path)
    gdf = gpd.read_parquet(tmp_path / "data/interim/fuente_prueba/2026.parquet")
    assert "CODMANPRE" in gdf.columns


def test_reads_inside_a_zip(tmp_path: Path, gpkg: Path) -> None:
    archive = gpkg.with_suffix(".zip")
    with zipfile.ZipFile(archive, "w") as zf:
        zf.write(gpkg, "carpeta/manzanas.gpkg")
    out = tmp_path / "out.parquet"
    stats = convert.to_geoparquet(archive, out, member="carpeta/manzanas.gpkg")
    assert stats["rows"] == 2
    assert gpd.read_parquet(out).crs.to_epsg() == 9377


@pytest.mark.filterwarnings("ignore:'crs' was not provided")
def test_missing_crs_fails(tmp_path: Path) -> None:
    src = tmp_path / "sin_crs.gpkg"
    gpd.GeoDataFrame({"a": [1]}, geometry=[Point(0, 0)]).to_file(src, driver="GPKG")
    with pytest.raises(MissingCRS):
        convert.to_geoparquet(src, tmp_path / "out.parquet")


@pytest.mark.filterwarnings("ignore:'crs' was not provided")
def test_assume_crs_only_fills_a_missing_crs(tmp_path: Path) -> None:
    src = tmp_path / "sin_crs.gpkg"
    gpd.GeoDataFrame({"a": [1]}, geometry=POINTS[:1]).to_file(src, driver="GPKG")
    stats = convert.to_geoparquet(src, tmp_path / "out.parquet", assume_crs="EPSG:4686")
    assert stats["crs_in"] == "EPSG:4686"


def test_counts_invalid_geometries_without_fixing_them(tmp_path: Path) -> None:
    from shapely.geometry import Polygon

    bowtie = Polygon([(-74.0, 4.6), (-73.9, 4.7), (-73.9, 4.6), (-74.0, 4.7)])
    src = tmp_path / "invalida.gpkg"
    gpd.GeoDataFrame({"a": [1]}, geometry=[bowtie], crs=4686).to_file(src, driver="GPKG")
    stats = convert.to_geoparquet(src, tmp_path / "out.parquet")
    assert stats["invalid_geometries"] == 1
    assert not gpd.read_parquet(tmp_path / "out.parquet").is_valid.iloc[0]
