"""DANE census blocks: Bogotá filter and arrival figures, on a tiny fake national file."""

import zipfile
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import box

from bogota_pop.ingest import dane_mgn
from bogota_pop.ingest.registry import converter_for


@pytest.fixture
def national_zip(tmp_path: Path) -> Path:
    """Three blocks shaped like DANE's file: two in Bogotá (11), one in Antioquia (05)."""
    gdf = gpd.GeoDataFrame(
        {
            "COD_DANE_A": [
                "1100110000000000000001",
                "1100110000000000000002",
                "0500110000000000000001",
            ],
            "DPTO_CCDGO": ["11", "11", "05"],
            "TP27_PERSO": [120.0, 0.0, 50.0],
            "TVIVIENDA": [40.0, 3.0, 20.0],
        },
        geometry=[
            box(-74.08, 4.60, -74.07, 4.61),
            box(-74.07, 4.60, -74.06, 4.61),
            box(-75.57, 6.24, -75.56, 6.25),
        ],
        crs=4326,
    )
    gpkg = tmp_path / dane_mgn.MEMBER
    gdf.to_file(gpkg, driver="GPKG")
    archive = tmp_path / "MGN_ANM_MANZANA_(Geopackage).zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.write(gpkg, dane_mgn.MEMBER)
    return archive


def test_keeps_bogota_only_and_reports_arrival_figures(tmp_path: Path, national_zip: Path) -> None:
    out = tmp_path / "out.parquet"
    stats = dane_mgn.convert(national_zip, out)
    gdf = gpd.read_parquet(out)
    assert set(gdf["DPTO_CCDGO"]) == {"11"}
    assert gdf.crs.to_epsg() == 9377
    assert stats["rows"] == 2
    assert stats["crs_in"] == "EPSG:4326"
    assert stats["suma_TP27_PERSO"] == 120
    assert stats["manzanas_sin_personas"] == 1
    assert stats["manzanas_con_viviendas_sin_personas"] == 1


def test_registry_routes_mgn_to_its_module() -> None:
    assert converter_for(dane_mgn.SOURCE_ID) is dane_mgn.convert


@pytest.fixture
def clase_zip(tmp_path: Path) -> Path:
    """Bogotá's three clases plus one Antioquia clase, shaped like DANE's file."""
    gdf = gpd.GeoDataFrame(
        {
            "DPTO_CCDGO": ["11", "11", "11", "05"],
            "CLAS_CCDGO": ["1", "2", "3", "1"],
            "STP27_PERS": [1000.0, 20.0, 5.0, 300.0],
            "STPERSON_L": [30.0, 0.0, 1.0, 10.0],
            "STPERSON_S": [970.0, 20.0, 4.0, 290.0],
        },
        geometry=[
            box(-74.10, 4.60, -74.05, 4.65),
            box(-74.20, 4.40, -74.19, 4.41),
            box(-74.30, 4.00, -74.10, 4.30),
            box(-75.60, 6.20, -75.50, 6.30),
        ],
        crs=4326,
    )
    gpkg = tmp_path / dane_mgn.CLASE_MEMBER
    gdf.to_file(gpkg, driver="GPKG")
    archive = tmp_path / "MGN_ANM_MPIOCL_(Geopackage).zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.write(gpkg, dane_mgn.CLASE_MEMBER)
    return archive


def test_clase_keeps_bogota_and_reports_persons_per_clase(tmp_path: Path, clase_zip: Path) -> None:
    out = tmp_path / "clase.parquet"
    stats = dane_mgn.convert_clase(clase_zip, out)
    assert gpd.read_parquet(out).crs.to_epsg() == 9377
    assert stats["rows"] == 3
    assert stats["suma_STP27_PERS"] == 1025
    assert stats["suma_STPERSON_L"] == 31
    assert stats["por_clase"]["3"] == {"STP27_PERS": 5, "STPERSON_L": 1, "STPERSON_S": 4}


def test_registry_routes_clase_to_its_converter() -> None:
    assert converter_for(dane_mgn.CLASE_SOURCE_ID) is dane_mgn.convert_clase
