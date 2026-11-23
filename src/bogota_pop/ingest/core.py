"""Ingest one source end to end: download, check fingerprint, convert, record.

The steps follow ADR-0012:

1. With ``--strict``, refuse a source that has no pinned fingerprint.
2. If we already have a copy matching the pin, use it (unless ``force``).
3. Otherwise download to a ``.part`` file and take its fingerprint.
4. Pinned and different: set the file aside in ``data/raw/_rejected/`` and stop.
   Not pinned: warn, print the fingerprint, continue.
5. Convert to ``data/interim/{source_id}/{vigencia}.parquet`` in EPSG:9377.
6. Write the receipt to ``config/manifest.json``.

Sources that need special handling (a layer name, a file inside a zip, a CRS the
file forgets to declare) pass a ``convert`` function; see each source's module.
"""

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from bogota_pop.ingest import convert as convert_mod
from bogota_pop.ingest import download, manifest
from bogota_pop.ingest.errors import (
    ChecksumMismatch,
    IngestError,
    NoDownloadUrl,
    UnpinnedSource,
)
from bogota_pop.ingest.sources import Source

log = logging.getLogger(__name__)

DATA_DIR = Path("data")

# Takes the raw file and the output path; returns rows / crs_in / crs_out / invalid_geometries.
Converter = Callable[[Path, Path], dict]


def raw_path(source: Source, data_dir: Path = DATA_DIR) -> Path:
    """``data/raw/{source_id}/{vigencia}/<file name from the URL>``."""
    name = download.filename_from_url(source.download_url)
    return data_dir / "raw" / source.id / source.vigencia / name


def interim_path(source: Source, data_dir: Path = DATA_DIR) -> Path:
    """``data/interim/{source_id}/{vigencia}.parquet``."""
    return data_dir / "interim" / source.id / f"{source.vigencia}.parquet"


def ingest_source(
    source: Source,
    *,
    data_dir: Path = DATA_DIR,
    manifest_path: Path = manifest.MANIFEST_JSON,
    strict: bool = False,
    force: bool = False,
    convert: Converter = convert_mod.to_geoparquet,
) -> dict:
    """Run every ingest step for one source; return its manifest entry."""
    if not source.download_url:
        raise NoDownloadUrl(f"{source.id}: download_url is empty in sources.yaml")
    if not source.vigencia:
        raise IngestError(f"{source.id}: vigencia is empty in sources.yaml")
    if strict and not source.sha256:
        raise UnpinnedSource(f"{source.id}: no sha256 pinned in sources.yaml (--strict)")

    raw = raw_path(source, data_dir)
    if not force and source.sha256 and raw.exists() and download.sha256_file(raw) == source.sha256:
        log.info("%s: using the copy already in %s", source.id, raw)
        sha = source.sha256
    else:
        log.info("%s: downloading %s", source.id, source.download_url)
        part, sha = download.fetch(source.download_url, raw)
        _check_fingerprint(source, part, raw, sha, data_dir)
        download.move(part, raw)

    out = interim_path(source, data_dir)
    stats = convert(raw, out)
    entry = {
        "url": source.download_url,
        "vigencia": source.vigencia,
        "downloaded_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sha256": sha,
        "pinned": bool(source.sha256),
        "size_bytes": raw.stat().st_size,
        "raw_path": raw.as_posix(),
        "interim_path": out.as_posix(),
        **stats,
    }
    if manifest.record(manifest_path, source.id, entry):
        log.info("%s: manifest updated", source.id)
    log.info("%s: %d rows written to %s", source.id, stats["rows"], out)
    return entry


def _check_fingerprint(source: Source, part: Path, raw: Path, sha: str, data_dir: Path) -> None:
    if source.sha256 is None:
        log.warning(
            "%s: not pinned. Fingerprint of this download:\n    sha256: %s\n"
            "Check the file, then pin it in config/sources.yaml (ADR-0012).",
            source.id,
            sha,
        )
        return
    if sha != source.sha256:
        rejected = data_dir / "raw" / "_rejected" / source.id / source.vigencia / raw.name
        download.move(part, rejected)
        raise ChecksumMismatch(
            f"{source.id}: the downloaded file is not the pinned one.\n"
            f"    expected: {source.sha256}\n"
            f"    got:      {sha}\n"
            f"The new file is in {rejected} for comparison. If the change is fine, "
            "update sha256 in config/sources.yaml and run again (ADR-0012)."
        )
