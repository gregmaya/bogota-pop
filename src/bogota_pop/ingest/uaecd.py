"""Bogotá's cadastre (UAECD): lots, buildings, blocks, land use and predios.

Five sources in config/sources.yaml: ``uaecd_lote``, ``uaecd_construccion``,
``uaecd_manzana``, ``uaecd_uso`` and ``uaecd_predio``.

Where it comes from
    Datos Abiertos Bogotá (datosabiertos.bogota.gov.co), one dataset page each,
    licence CC BY 4.0. UAECD publishes a new cut every month. Each month's file
    keeps its own address (the name ends in the month, e.g. ``.10.26`` for
    October 2026), so a pinned fingerprint stays valid.

How it is downloaded
    Plain downloads of static zips. Lote, Construcción and Manzana are
    shapefiles (EPSG:4326); Uso and Predio are CSV tables (UTF-8).
    All five must be the same monthly cut: the ``vigencia`` in sources.yaml
    says which one (``"2026-10"``), and a test checks that they agree.

What ingest does
    Zips kept untouched in data/raw. The three layers are reprojected to
    EPSG:9377 and written as GeoParquet; the two tables are written as plain
    Parquet with every column as text, so codes keep their leading zeros.
    Field names stay as UAECD publishes them.

Things to know
    - Every layer here is lot level or finer, so everything derived from it
      stays local (ADR-0006). Only block and H3 aggregates are published.
    - Predio has one row per property, with addresses and appraisal fields.
      Ingest keeps only the columns in ``PREDIO_COLUMNS``; the rest never
      reach data/interim.
    - The lot code has 12 characters and is named differently in each file:
      ``LOTCODIGO`` (Lote), ``LOTECODIGO`` (Construcción), ``USOCLOTE`` (Uso),
      ``BARMANPRE`` (Predio).
    - ``SHAPE_AREA`` and ``SHAPE_LEN`` in the shapefiles are in degrees, so
      they are useless. Areas are computed after reprojecting.
    - What the codes mean (``USOTUSO``, ``PRECDESTIN``, ``PRECLASE``) needs
      UAECD's data dictionary. Until it is found, ingest only counts raw values
      and never interprets them.
    - Nothing older than December 2019 (Predio), March 2020 (Uso) or
      December 2022 (the three layers) is online.
"""

from pathlib import Path

from bogota_pop.ingest.convert import table_to_parquet, to_geoparquet

LOTE_ID = "uaecd_lote"
CONSTRUCCION_ID = "uaecd_construccion"
MANZANA_ID = "uaecd_manzana"
USO_ID = "uaecd_uso"
PREDIO_ID = "uaecd_predio"
SOURCE_IDS = (LOTE_ID, CONSTRUCCION_ID, MANZANA_ID, USO_ID, PREDIO_ID)

LOTE_MEMBER = "LOTE.shp"
CONSTRUCCION_MEMBER = "CONST_V2.shp"
MANZANA_MEMBER = "MANZ.shp"
USO_MEMBER = "TUSO.csv"
PREDIO_MEMBER = "TPREDIO.csv"

# Kept from Predio: the lot and predio keys, use and destination codes, the
# PH and dwelling flags, areas, building age and the year field. Dropped:
# addresses, barrio, owner type, appraisal and construction-quality scores.
PREDIO_COLUMNS = [
    "BARMANPRE",
    "PRECHIP",
    "PRECLASE",
    "PRECDESTIN",
    "PRECUSO",
    "PREAUSO",
    "PREUSOPH",
    "PREUSONPH",
    "PREUVIVIEN",
    "PREATERRE",
    "PREACONST",
    "PREVETUSTZ",
    "PREVACTUAL",
]
# Raw values counted on arrival, without interpreting them.
PREDIO_COUNTED = ["PRECLASE", "PREUSOPH", "PREUVIVIEN", "PREVACTUAL"]


def _value_counts(series) -> dict[str, int]:
    counts = series.fillna("(vacío)").value_counts().sort_index()
    return {str(k): int(v) for k, v in counts.items()}


def convert_lote(raw: Path, out: Path) -> dict:
    """Write lots to GeoParquet (EPSG:9377); add ``lotes_codigo_unico``."""
    import pandas as pd

    stats = to_geoparquet(raw, out, member=LOTE_MEMBER)
    codes = pd.read_parquet(out, columns=["LOTCODIGO"])["LOTCODIGO"]
    return {**stats, "lotes_codigo_unico": int(codes.nunique())}


def convert_construccion(raw: Path, out: Path) -> dict:
    """Write buildings to GeoParquet (EPSG:9377); add lots with buildings, buildings ≥4 floors."""
    import pandas as pd

    stats = to_geoparquet(raw, out, member=CONSTRUCCION_MEMBER)
    df = pd.read_parquet(out, columns=["LOTECODIGO", "CONNPISOS"])
    return {
        **stats,
        "lotes_con_construccion": int(df["LOTECODIGO"].nunique()),
        "construcciones_4_pisos_o_mas": int((df["CONNPISOS"] >= 4).sum()),
    }


def convert_manzana(raw: Path, out: Path) -> dict:
    """Write cadastral blocks to GeoParquet (EPSG:9377); add ``manzanas_codigo_unico``."""
    import pandas as pd

    stats = to_geoparquet(raw, out, member=MANZANA_MEMBER)
    codes = pd.read_parquet(out, columns=["MANCODIGO"])["MANCODIGO"]
    return {**stats, "manzanas_codigo_unico": int(codes.nunique())}


def convert_uso(raw: Path, out: Path) -> dict:
    """Write the land-use table to Parquet (all text); add lots and use codes seen."""
    import pandas as pd

    stats = table_to_parquet(raw, out, member=USO_MEMBER)
    df = pd.read_parquet(out, columns=["USOCLOTE", "USOTUSO"])
    return {
        **stats,
        "lotes_unicos": int(df["USOCLOTE"].nunique()),
        "codigos_USOTUSO": int(df["USOTUSO"].nunique()),
    }


def convert_predio(raw: Path, out: Path) -> dict:
    """Write the predio table to Parquet, keeping only ``PREDIO_COLUMNS`` (all text).

    Adds ``lotes_unicos`` and, for each field in ``PREDIO_COUNTED``, the count
    of each raw value (``conteo_<field>``).
    """
    import pandas as pd

    stats = table_to_parquet(raw, out, member=PREDIO_MEMBER, columns=PREDIO_COLUMNS)
    df = pd.read_parquet(out, columns=["BARMANPRE", *PREDIO_COUNTED])
    return {
        **stats,
        "lotes_unicos": int(df["BARMANPRE"].nunique()),
        **{f"conteo_{field}": _value_counts(df[field]) for field in PREDIO_COUNTED},
    }


CONVERTERS = {
    LOTE_ID: convert_lote,
    CONSTRUCCION_ID: convert_construccion,
    MANZANA_ID: convert_manzana,
    USO_ID: convert_uso,
    PREDIO_ID: convert_predio,
}
