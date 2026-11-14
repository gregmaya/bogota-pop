"""Smoke tests for the geospatial stack: GDAL, PROJ, EPSG:9377, GeoParquet, DuckDB spatial.

These run in CI on every OS in the matrix, so an install problem shows up as a failing
test rather than as a confusing error deep inside a pipeline stage.
"""

from pathlib import Path

import duckdb
import geopandas as gpd
import h3
import pyproj
import pytest
from shapely.geometry import Point

# Plaza de Bolívar, WGS84 (lon, lat)
PLAZA_BOLIVAR = (-74.0761, 4.5981)


@pytest.fixture
def plaza(tmp_path: Path):
    """A one-point GeoDataFrame in EPSG:9377, written to GeoParquet and GeoPackage."""
    gdf = gpd.GeoDataFrame({"n": [1]}, geometry=[Point(*PLAZA_BOLIVAR)], crs=4326).to_crs(9377)
    gdf.to_parquet(tmp_path / "plaza.parquet")
    gdf.to_file(tmp_path / "plaza.gpkg")
    return gdf, tmp_path


def test_epsg_9377_is_known_to_proj() -> None:
    assert pyproj.CRS.from_epsg(9377).name == "MAGNA-SIRGAS 2018 / Origen-Nacional"


def test_reprojection_lands_in_bogota(plaza) -> None:
    gdf, _ = plaza
    x, y = gdf.geometry.x.iloc[0], gdf.geometry.y.iloc[0]
    # Origen Nacional false origin is (5,000,000, 2,000,000); Bogotá sits just west and north.
    assert 4_870_000 < x < 4_890_000
    assert 2_050_000 < y < 2_080_000


def test_geoparquet_and_gpkg_keep_crs(plaza) -> None:
    _, d = plaza
    assert gpd.read_parquet(d / "plaza.parquet").crs.to_epsg() == 9377
    assert gpd.read_file(d / "plaza.gpkg").crs.to_epsg() == 9377


def test_duckdb_spatial_reads_gpkg(plaza) -> None:
    _, d = plaza
    con = duckdb.connect()
    con.install_extension("spatial")
    con.load_extension("spatial")
    area = con.execute("SELECT ST_Area(ST_Buffer(ST_Point(0, 0), 1))").fetchone()[0]
    assert area == pytest.approx(3.12, abs=0.05)  # buffer is a polygon approximating pi
    rows = con.execute(f"SELECT count(*) FROM ST_Read('{d / 'plaza.gpkg'}')").fetchone()[0]
    assert rows == 1


def test_h3_resolution_9_cell() -> None:
    lon, lat = PLAZA_BOLIVAR
    cell = h3.latlng_to_cell(lat, lon, 9)
    assert h3.get_resolution(cell) == 9
