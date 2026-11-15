"""Keep config/sources.yaml in the agreed layout (schema_version 1)."""

import re
from pathlib import Path

import pytest
import yaml

SOURCES_YAML = Path(__file__).parents[1] / "config" / "sources.yaml"

FIELDS = {
    "title",
    "publisher",
    "priority",
    "first_used",
    "used_for",
    "landing_page",
    "download_url",
    "format",
    "vigencia",
    "licence",
    "access",
    "sha256",
    "checks",
}
PRIORITIES = {"core", "v2", "validation", "comparison", "scenarios"}
ACCESS = {"public", "request", "restricted", None}
PHASES = {f"phase_{n}" for n in range(1, 7)}

config = yaml.safe_load(SOURCES_YAML.read_text(encoding="utf-8"))
sources: dict = config["sources"]


def test_schema_version() -> None:
    assert config["schema_version"] == 1


@pytest.mark.parametrize("source_id", sorted(sources))
def test_source_entry(source_id: str) -> None:
    entry = sources[source_id]
    assert re.fullmatch(r"[a-z][a-z0-9_]*", source_id), "IDs are snake_case"
    assert set(entry) == FIELDS, f"fields differ: {set(entry) ^ FIELDS}"
    assert entry["title"], "title is required"
    assert entry["used_for"], "used_for is required"
    assert entry["priority"] in PRIORITIES
    assert entry["first_used"] in PHASES
    assert entry["access"] in ACCESS
    for key in ("landing_page", "download_url"):
        assert entry[key] is None or entry[key].startswith("https://"), f"{key} must be https"
    assert entry["sha256"] is None or re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])
    assert isinstance(entry["checks"], list)
    assert entry["checks"], "at least one check on arrival"
