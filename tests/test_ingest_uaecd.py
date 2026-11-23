"""UAECD cadastre: converters on tiny fake files shaped like the real ones."""

import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from bogota_pop.ingest import uaecd
from bogota_pop.ingest.registry import converter_for
from bogota_pop.ingest.sources import load_sources


def _shp_zip(tmp_path: Path, gdf: gpd.GeoDataFrame, member: str) -> Path:
    """Write ``gdf`` as a shapefile named ``member`` and zip all its parts."""
    folder = tmp_path / "shp"
    folder.mkdir()
    gdf.to_file(folder / member, driver="ESRI Shapefile")
    archive = tmp_path / f"{Path(member).stem}.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for part in folder.iterdir():
            zf.write(part, part.name)
    return archive


def _csv_zip(tmp_path: Path, text: str, member: str) -> Path:
    archive = tmp_path / f"{Path(member).stem}.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(member, text)
    return archive


def test_lote_reprojects_and_counts_codes(tmp_path: Path) -> None:
    gdf = gpd.GeoDataFrame(
        {"LOTCODIGO": ["008519073023", "008519001008", "008519001008"]},
        geometry=[box(-74.08, 4.60, -74.079, 4.601)] * 3,
        crs=4326,
    )
    out = tmp_path / "lote.parquet"
    stats = uaecd.convert_lote(_shp_zip(tmp_path, gdf, uaecd.LOTE_MEMBER), out)
    assert gpd.read_parquet(out).crs.to_epsg() == 9377
    assert stats["rows"] == 3
    assert stats["lotes_codigo_unico"] == 2


def test_construccion_counts_lots_and_tall_buildings(tmp_path: Path) -> None:
    gdf = gpd.GeoDataFrame(
        {"LOTECODIGO": ["003105012008", "003105012008", "003110001015"], "CONNPISOS": [1, 4, 12]},
        geometry=[box(-74.08, 4.60, -74.079, 4.601)] * 3,
        crs=4326,
    )
    stats = uaecd.convert_construccion(
        _shp_zip(tmp_path, gdf, uaecd.CONSTRUCCION_MEMBER), tmp_path / "c.parquet"
    )
    assert stats["lotes_con_construccion"] == 2
    assert stats["construcciones_4_pisos_o_mas"] == 2


def test_uso_keeps_leading_zeros(tmp_path: Path) -> None:
    text = 'USOCLOTE,USOTUSO,USOAREA\n"001424030002","001",114.58\n"001424030002","038",20.0\n'
    out = tmp_path / "uso.parquet"
    stats = uaecd.convert_uso(_csv_zip(tmp_path, text, uaecd.USO_MEMBER), out)
    df = pd.read_parquet(out)
    assert list(df["USOTUSO"]) == ["001", "038"]
    assert stats == {
        "rows": 2,
        "columns_kept": ["USOCLOTE", "USOTUSO", "USOAREA"],
        "lotes_unicos": 1,
        "codigos_USOTUSO": 2,
    }


def test_predio_drops_addresses_and_counts_raw_values(tmp_path: Path) -> None:
    header = ["PREDIRECC", *uaecd.PREDIO_COLUMNS, "PREPUNTAJE"]
    lot_a, lot_b = "001101009001", "001101009002"
    rows = [
        {"PREDIRECC": "KR 7 6 16", "BARMANPRE": lot_a, "PREUSOPH": "S", "PREVACTUAL": "2026"},
        {"PREDIRECC": "KR 7 6 18", "BARMANPRE": lot_a, "PREUSOPH": "N", "PREVACTUAL": "2026"},
        {"PREDIRECC": "CL 1 2 3", "BARMANPRE": lot_b, "PREUSOPH": "", "PREVACTUAL": "2026"},
    ]
    text = pd.DataFrame(rows, columns=header).to_csv(index=False)
    out = tmp_path / "predio.parquet"
    stats = uaecd.convert_predio(_csv_zip(tmp_path, text, uaecd.PREDIO_MEMBER), out)
    df = pd.read_parquet(out)
    assert list(df.columns) == uaecd.PREDIO_COLUMNS
    assert "PREDIRECC" not in df.columns
    assert stats["lotes_unicos"] == 2
    assert stats["conteo_PREUSOPH"] == {"(vacío)": 1, "N": 1, "S": 1}
    assert stats["conteo_PREVACTUAL"] == {"2026": 3}


def test_all_uaecd_sources_share_one_cut() -> None:
    """All five cadastre files must come from the same monthly cut."""
    sources = load_sources()
    cuts = {sid: sources[sid].vigencia for sid in uaecd.SOURCE_IDS}
    assert len(set(cuts.values())) == 1, cuts


@pytest.mark.parametrize("source_id", uaecd.SOURCE_IDS)
def test_registry_routes_uaecd_sources(source_id: str) -> None:
    assert converter_for(source_id) is uaecd.CONVERTERS[source_id]
