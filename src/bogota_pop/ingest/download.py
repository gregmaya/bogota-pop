"""Download a file and take its fingerprint (SHA-256) while it streams.

Uses only the standard library (urllib), which also reads ``file://`` URLs:
that is how the tests run without network.

The file is written to ``<name>.part``. The caller decides, after checking the
fingerprint, whether it becomes the real file or is set aside (ADR-0012).
"""

import hashlib
import logging
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

from bogota_pop.ingest.errors import DownloadFailed

log = logging.getLogger(__name__)

CHUNK_BYTES = 1024 * 1024
TIMEOUT_SECONDS = 120
RETRIES = 3
USER_AGENT = "bogota-pop ingest (+https://github.com/gregmaya/bogota-pop)"


def sha256_file(path: Path) -> str:
    """Return the SHA-256 fingerprint of a file on disk, as 64 hex characters."""
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def filename_from_url(url: str) -> str:
    """Last part of the URL path, e.g. ``.../MGN_2018.zip`` -> ``MGN_2018.zip``."""
    name = PurePosixPath(unquote(urlparse(url).path)).name
    if not name:
        raise DownloadFailed(f"cannot tell a file name from {url}; give one explicitly")
    return name


def part_path(dest: Path) -> Path:
    """Where a download in progress is written: ``dest`` plus ``.part``."""
    return dest.with_name(dest.name + ".part")


def fetch(
    url: str, dest: Path, *, retries: int = RETRIES, backoff_seconds: float = 2.0
) -> tuple[Path, str]:
    """Download ``url`` to ``dest.part``; return that path and its SHA-256.

    Retries on network errors, waiting a little longer each time. Raises
    DownloadFailed when every attempt fails; no ``.part`` file is left behind.
    """
    part = part_path(dest)
    part.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, retries + 1):
        try:
            digest = hashlib.sha256()
            with (
                urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response,
                part.open("wb") as out,
            ):
                while chunk := response.read(CHUNK_BYTES):
                    digest.update(chunk)
                    out.write(chunk)
            return part, digest.hexdigest()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as err:
            part.unlink(missing_ok=True)
            if attempt == retries:
                raise DownloadFailed(f"{url}: {err} (tried {retries} times)") from err
            wait = backoff_seconds * attempt
            log.warning("download failed (%s), retrying in %.0f s", err, wait)
            time.sleep(wait)
    raise AssertionError("unreachable")


def move(src: Path, dest: Path) -> None:
    """Move a file, creating the destination folder and replacing any old file."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src, dest)
