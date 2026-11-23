"""Errors raised by ingest. The CLI turns each one into a one-line message and exit code 1."""


class IngestError(Exception):
    """Base class: something stopped a source from being ingested."""


class UnknownSource(IngestError):
    """The source id is not in config/sources.yaml."""


class NoDownloadUrl(IngestError):
    """The source has no download_url yet, so there is nothing to fetch."""


class DownloadFailed(IngestError):
    """The file could not be downloaded, even after retrying."""


class ChecksumMismatch(IngestError):
    """The downloaded file's fingerprint differs from the pinned one (ADR-0012)."""


class UnpinnedSource(IngestError):
    """The source has no pinned fingerprint and --strict was given (ADR-0012)."""


class MissingCRS(IngestError):
    """The layer declares no CRS and none was given with assume_crs."""
