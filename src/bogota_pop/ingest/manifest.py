"""config/manifest.json: the receipt of what was actually downloaded (ADR-0012).

One entry per source. An entry is rewritten only when something other than the
download date changed, so re-running ingest on the same data leaves git clean.
"""

import fcntl
import json
import os
from contextlib import contextmanager
from pathlib import Path

MANIFEST_JSON = Path("config/manifest.json")
SCHEMA_VERSION = 1
# Fields that change on every run without the data changing.
VOLATILE = {"downloaded_at"}


def read(path: Path = MANIFEST_JSON) -> dict:
    """Return the manifest, or an empty one if the file does not exist yet."""
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "sources": {}}
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def _locked(path: Path):
    """Hold a lock on ``path`` so parallel Snakemake jobs don't overwrite each other."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path.with_name(path.name + ".lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def record(path: Path, source_id: str, entry: dict) -> bool:
    """Store ``entry`` for ``source_id``; return True if the file changed.

    Leaves the file untouched when the new entry only differs in volatile fields.
    """
    with _locked(path):
        data = read(path)
        old = data["sources"].get(source_id)
        if old is not None and _stable(old) == _stable(entry):
            return False
        data["sources"][source_id] = entry
        data["sources"] = dict(sorted(data["sources"].items()))
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        return True


def _stable(entry: dict) -> dict:
    return {k: v for k, v in entry.items() if k not in VOLATILE}
