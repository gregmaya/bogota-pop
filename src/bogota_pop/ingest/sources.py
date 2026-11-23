"""Read config/sources.yaml: what we expect to download (ADR-0012).

Paths are relative to the repo root; the CLI and Snakemake both run from there.
"""

from dataclasses import dataclass
from pathlib import Path

import yaml

from bogota_pop.ingest.errors import UnknownSource

SOURCES_YAML = Path("config/sources.yaml")


@dataclass(frozen=True)
class Source:
    """The fields of one sources.yaml entry that ingest needs."""

    id: str
    title: str
    download_url: str | None
    vigencia: str | None
    sha256: str | None


def load_sources(path: Path = SOURCES_YAML) -> dict[str, Source]:
    """Return every source in sources.yaml, keyed by id."""
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {
        source_id: Source(
            id=source_id,
            title=entry["title"],
            download_url=entry["download_url"],
            vigencia=None if entry["vigencia"] is None else str(entry["vigencia"]),
            sha256=entry["sha256"],
        )
        for source_id, entry in config["sources"].items()
    }


def get_source(source_id: str, sources: dict[str, Source]) -> Source:
    """Look up one source; raise UnknownSource with the valid ids if it is missing."""
    try:
        return sources[source_id]
    except KeyError:
        raise UnknownSource(
            f"'{source_id}' is not in sources.yaml. Known ids: {', '.join(sorted(sources))}"
        ) from None
