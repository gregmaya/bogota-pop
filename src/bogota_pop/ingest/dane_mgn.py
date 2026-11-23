"""DANE census geography: MGN 2018 integrated with the 2018 census (CNPV 2018).

Two sources in config/sources.yaml, from the same DANE product:
``dane_mgn_cnpv2018_manzana`` (blocks) and ``dane_mgn_cnpv2018_clase``
(each municipality split into its three clases). The notes below are for the
blocks; the clase layer has its own notes further down.

Where it comes from
    DANE's geoportal, "MGN-Nivel Manzana integrado con variables del CNPV2018".
    One national file: a zip with a single GeoPackage inside,
    ``MGN_ANM_MANZANA (Geopackage).gpkg`` (about 505,000 blocks, EPSG:4326).
    Field descriptions: DANE's "instructivo de uso" (see landing_page).

How it is downloaded
    A plain download of a static file (~324 MB). The geoportal refuses
    Python's default user agent (HTTP 403); ours is accepted.

What ingest does
    Keeps the national zip untouched in data/raw (the fingerprint is of that
    file). Reads only Bogotá (``DPTO_CCDGO = '11'``) into data/interim,
    reprojected to EPSG:9377. Field names stay as DANE publishes them.

Things to know
    - Population per block is ``TP27_PERSO``. The ``STP27_PERS`` name only
      exists in DANE's department and municipality layers.
    - ``DATO_ANM`` is not an "anonymised" flag. It names the level the block's
      data is published at, and is ``MANZANA`` for every Bogotá block.
      Blocks whose counts DANE moved up show 0 persons instead.
    - People in group quarters (LEA: prisons, barracks, care homes) and in
      anonymised blocks are not in any block. DANE publishes them one level
      up, in the "clase" layer. So the block total is below the census total.
"""

from pathlib import Path

from bogota_pop.ingest.convert import to_geoparquet

SOURCE_ID = "dane_mgn_cnpv2018_manzana"
MEMBER = "MGN_ANM_MANZANA (Geopackage).gpkg"
# Bogotá only, for now. Widening this (e.g. to neighbouring municipalities) is
# an open question recorded in docs/plan.md.
WHERE = "DPTO_CCDGO = '11'"


def convert(raw: Path, out: Path) -> dict:
    """Write Bogotá's blocks to GeoParquet; return the usual stats plus arrival figures.

    Arrival figures (from sources.yaml ``checks``), named in Spanish like the data:
    ``suma_TP27_PERSO``, ``manzanas_sin_personas``, ``manzanas_con_viviendas_sin_personas``.
    """
    import pandas as pd

    stats = to_geoparquet(raw, out, member=MEMBER, where=WHERE)
    df = pd.read_parquet(out, columns=["TP27_PERSO", "TVIVIENDA"])
    sin_personas = df["TP27_PERSO"].fillna(0) == 0
    return {
        **stats,
        "suma_TP27_PERSO": int(df["TP27_PERSO"].sum()),
        "manzanas_sin_personas": int(sin_personas.sum()),
        "manzanas_con_viviendas_sin_personas": int((sin_personas & (df["TVIVIENDA"] > 0)).sum()),
    }


# ── Clase layer ───────────────────────────────────────────────────────────────
# Where it comes from
#     Same geoportal page: "MGN-Nivel Municipio-Clase integrado con variables
#     del CNPV2018". A zip with ``MGN_ANM_MPIOCL (Geopackage).gpkg`` inside
#     (~110 MB, 3,155 rows for the whole country, EPSG:4326).
#
# What ingest does
#     Same as the blocks: zip kept untouched in data/raw, Bogotá only
#     (three rows) in data/interim, reprojected to EPSG:9377.
#
# Things to know
#     - Field names here start with S ("suma"): ``STP27_PERS`` is all persons,
#       ``STPERSON_L`` those in group quarters (LEA), ``STPERSON_S`` the rest.
#     - Clase 3 (rural disperso) has no blocks, so its people are only here.

CLASE_SOURCE_ID = "dane_mgn_cnpv2018_clase"
CLASE_MEMBER = "MGN_ANM_MPIOCL (Geopackage).gpkg"
CLASE_FIELDS = ["STP27_PERS", "STPERSON_L", "STPERSON_S"]


def convert_clase(raw: Path, out: Path) -> dict:
    """Write Bogotá's clase rows to GeoParquet; return the usual stats plus arrival figures.

    Arrival figures: ``por_clase`` maps each ``CLAS_CCDGO`` to its persons
    (``STP27_PERS``, ``STPERSON_L``, ``STPERSON_S``), and the city totals
    of the same fields are given as ``suma_<field>``.
    """
    import pandas as pd

    stats = to_geoparquet(raw, out, member=CLASE_MEMBER, where=WHERE)
    df = pd.read_parquet(out, columns=["CLAS_CCDGO", *CLASE_FIELDS]).sort_values("CLAS_CCDGO")
    return {
        **stats,
        **{f"suma_{field}": int(df[field].sum()) for field in CLASE_FIELDS},
        "por_clase": {
            str(row.CLAS_CCDGO): {field: int(getattr(row, field)) for field in CLASE_FIELDS}
            for row in df.itertuples()
        },
    }
