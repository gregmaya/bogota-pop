# ADR-0012: Ingest provenance: checksums and manifest

- **Status:** Accepted
- **Date:** 2026-11-15
- **Plan reference:** Phase 1 tasks and the "Sources change format or URL between vigencias" risk in [docs/plan.md](../plan.md)

## Context

Every result depends on files downloaded from public portals (DANE, UAECD, SDP). Those files can change without notice: corrected numbers, a new vigencia under the same URL, a broken export. If a change slips in quietly, the population estimates move and nobody can say why.

We need two things. First, a way to notice when a file is not the one we checked before. Second, a record of exactly which files each run and each release was built from.

## Decision

### The idea in one picture

A **checksum** (SHA-256) is a file's fingerprint: a 64-character code computed from its content. The same file always gives the same fingerprint. Change one comma and the fingerprint is completely different. Comparing fingerprints tells us whether two files are identical without opening them.

Think of each source as a book we rely on. The first time we get it, a person checks it and takes a photo of its fingerprint. That photo is the **pin**. On every later download we compare the new copy's fingerprint with the photo.

### Two files, two jobs

| File | Holds | Written by | Committed |
| --- | --- | --- | --- |
| `config/sources.yaml` (`sha256` field) | **What we expect**: URL, vigencia, the pinned fingerprint | A person, on purpose | Yes |
| `config/manifest.json` | **What actually happened**: URL, vigencia, download date, fingerprint, size, rows, CRS before and after, file paths | The code, on every download | Yes |

`sources.yaml` is the order. `manifest.json` is the receipt.

### What ingest does in each case

| Situation | In plain words | Behaviour |
| --- | --- | --- |
| Pinned, fingerprint matches | Same book as last time | Continue |
| Pinned, fingerprint differs | The source changed without telling us | **Stop with an error.** The new file is set aside in `data/raw/_rejected/` for comparison. Nothing downstream runs. If the change is fine, a person updates the pin and runs again |
| Not pinned yet (`sha256: null`) | First time; no photo to compare against | Download, print the fingerprint and say "check the file, then pin this". With `--strict`, stop instead |
| Already in `data/raw/` and matches the pin | We already have this exact copy | Skip the download. `--force` downloads again |

### Small rules that keep it tidy

- Fingerprints are taken of the file **exactly as downloaded** (the zip, not what's inside it).
- A download is written to a temporary `.part` file and only renamed once it is complete and checked. A half-finished download never looks like a real file.
- A manifest entry is rewritten **only when the fingerprint changes**. Running ingest again on the same data leaves `manifest.json` untouched, so git shows a change only when the data really changed.
- `--strict` is for releases and CI once sources are pinned. Day-to-day work runs without it, so new sources can be explored (MVP first).

## Alternatives considered

- **No checksums; trust URL and vigencia.** Simpler, but a quiet change at the source goes straight into the results.
- **Manifest in `data/` (local only).** Nothing shared would record which files a release used, so results could not be traced back to their inputs.
- **Fail on unpinned sources by default.** Safer, but it would block the first download of every new source and slow down exploration.

## Consequences

- Each source needs one human step: check the first download, then copy its fingerprint into `sources.yaml`.
- An updated source stops the pipeline until someone looks at it. This is intended: it turns a silent change into a visible decision.
- `config/manifest.json` shows up in commits whenever data changes. Reviewing that diff is how we see what changed between releases.
- **Open item:** some portals (ArcGIS Hub, some CKAN exports) rebuild their zip on every download and stamp a new date inside it. The data is the same, but the fingerprint changes every time, like the same book reprinted with today's date on the first page. If a source does this, we fingerprint the data inside the zip instead, and note it in that source's documentation. Decide per source when it happens.
