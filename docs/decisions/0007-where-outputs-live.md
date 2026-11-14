# ADR-0007: Outputs on GitHub Releases, Zenodo DOI for major releases

- **Status:** Accepted
- **Date:** 2026-11-14
- **Plan reference:** D7 in [docs/plan.md](../plan.md)

## Context

Data never lives in git history. Users still need versioned, downloadable, citable outputs, and other projects need to pin a specific version.

## Decision

- Each version is a GitHub Release: a tagged snapshot of the repo (tagged by cadastral vigencia, for example `v2026.1`) with output files attached.
- The repo is linked to Zenodo, which archives each Release automatically; major releases are cited by their Zenodo DOI.
- Development stage tiles ship as GitHub pre-releases tagged by date (`dev-YYYY-MM-DD`).

## Alternatives considered

- **Git LFS** — puts data in the repo's storage quota and complicates clones.
- **Object storage (S3 / R2) only** — flexible, but no built-in versioning-to-code link and no DOI.
- **Datos Abiertos Bogotá / institutional portal** — a good future mirror, but not under the project's control.

## Consequences

- Release assets are limited to 2 GB per file; outputs must stay within that (GeoParquet compresses well).
- `CITATION.cff` must be kept current so Zenodo metadata is correct.
- The viewer pins a release tag, so a new release never breaks it until bumped deliberately.
