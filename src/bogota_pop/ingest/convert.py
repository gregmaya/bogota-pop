"""Turn a downloaded file into GeoParquet in EPSG:9377 (CLAUDE.md rules 4 and 5).

Field names are kept exactly as published. Geometries are not repaired here:
invalid ones are counted, logged and left for harmonise to deal with.
"""

import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)

TARGET_CRS = "EPSG:9377"  # MAGNA-SIRGAS Origen Nacional


def gdal_path(raw: Path, member: str | None = None) -> str:
    """Path GDAL can open. ``member`` is a file inside a zip, read without unzipping."""
    if member is None:
        return str(raw)
    return f"/vsizip/{raw.resolve()}/{member}"


def to_geoparquet(
    raw: Path,
    out: Path,
    *,
    layer: str | None = None,
    member: str | None = None,
    where: str | None = None,
    assume_crs: str | None = None,
) -> dict:
    """Read a vector layer, reproject it to EPSG:9377 and write GeoParquet.

    ``layer`` picks a layer in multi-layer files (GeoPackage, File Geodatabase).
    ``where`` is an SQL filter on source fields, e.g. ``"DPTO_CCDGO = '11'"``;
    rows that don't match are never loaded.
    ``assume_crs`` is used only when the file declares no CRS; it never overrides one.
    Returns ``rows``, ``crs_in``, ``crs_out`` and ``invalid_geometries``.
    """
    import geopandas as gpd  # heavy; keep `bogota-pop --help` fast (ADR-0009)

    from bogota_pop.ingest.errors import MissingCRS

    gdf = gpd.read_file(gdal_path(raw, member), layer=layer, where=where, engine="pyogrio")
    if gdf.crs is None:
        if assume_crs is None:
            raise MissingCRS(f"{raw.name} declares no CRS; pass assume_crs if it is known")
        gdf = gdf.set_crs(assume_crs)
    crs_in = _crs_name(gdf.crs)
    gdf = gdf.to_crs(TARGET_CRS)

    invalid = int((~gdf.geometry.is_valid & gdf.geometry.notna()).sum())
    if invalid:
        log.warning("%s: %d invalid geometries (kept as is for harmonise)", raw.name, invalid)

    tmp = out.with_name(out.name + ".part")
    out.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(tmp, compression="zstd", write_covering_bbox=True)
    os.replace(tmp, out)
    return {
        "rows": len(gdf),
        "crs_in": crs_in,
        "crs_out": TARGET_CRS,
        "invalid_geometries": invalid,
    }


def _crs_name(crs) -> str:
    epsg = crs.to_epsg()
    return f"EPSG:{epsg}" if epsg else crs.to_string()
