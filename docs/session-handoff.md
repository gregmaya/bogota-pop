# Session handoff

Updated 2026-11-15, at the close of Phase 0. Read this first in a new session, then only the files the next task needs. CLAUDE.md is already loaded automatically.

## Where things stand

- **Phase 0 is closed** and tagged `v0.0.1` (commit `c67c0b6`). CI is green on Ubuntu and macOS (lint, 33 tests, Snakemake pipeline run plus a "nothing to do" re-check).
- **Now: Phase 1, data acquisition.** Work is tracked on GitHub: one milestone per phase, issues [#1–#11](https://github.com/gregmaya/bogota-pop/issues). Each issue's checklist mirrors the tasks in `docs/plan.md`.
- **Next step:** issue **#1, first checklist item.** This is the shared download code: verify against the pinned `sha256` in `config/sources.yaml` (fail loudly on mismatch), record URL, vigencia, date and SHA-256 in `manifest.json`, reproject to EPSG:9377, write GeoParquet. Then replace the ingest marker in `pipeline/Snakefile` with real outputs. **Propose the design first and wait for approval** before writing code.

## Where to look

| Need | File |
| --- | --- |
| Rules, commands, conventions | `CLAUDE.md` |
| Full plan and phase checklists | `docs/plan.md` |
| Why things are the way they are | `docs/decisions/` (ADR-0001 to 0011; index in its README) |
| Every dataset, with TODOs to fill in Phase 1 | `config/sources.yaml` (layout enforced by `tests/test_sources_config.py`) |
| Acronyms and local terms, EN/ES | `docs/glossary.md` |
| CLI | `src/bogota_pop/cli.py` (Typer; stage commands are stubs that exit 0) |
| Pipeline | `pipeline/Snakefile` (rules call `bogota-pop <stage>`; `code()` lists stage sources as inputs) |
| CI | `.github/workflows/ci.yml` |

## Decisions taken in Phase 0 (beyond D1–D8)

- **uv**, not pixi. Python 3.12. GDAL 3.12 and PROJ 9.8 come in the wheels; DuckDB 2.0 with the spatial extension.
- **Typer** for the CLI (ADR-0009). **Snakemake** for orchestration (ADR-0010).
- **Bilingual GitHub** (ADR-0011): issues, PRs, milestones, labels and release notes in English and Spanish, titled `English · Español`. Every acronym is spelled out the first time, in each language. Code, comments, commits and ADRs stay in English.
- **Fewer, bigger issues:** one or two per milestone, with checklists. No due dates.
- **Tags vs Releases:** git tags mark milestones (`v0.0.1`). GitHub Releases are only for data versions, because Zenodo mints a DOI for each one. Release numbering is still open (issue #5).
- **Author:** Gregorio Maya (citation "Maya, Gregorio"), ORCID 0009-0002-8285-7253. No affiliation or funding.

## How Gregorio wants to work

- Talk each decision through before writing code. Stop after each step for review. Gregorio commits and pushes; Claude doesn't.
- End every step with the current phase's progress table (✅ / 🟡 with what's missing / ⏭️ / ⬜).
- Tick the box in `docs/plan.md` **and** the matching item in the GitHub issue checklist in the same change.
- Explain unfamiliar tools simply, with a recommendation, before asking for a choice.
- Anything public on GitHub (issues, labels, tags) gets a go-ahead first.

## Open questions waiting for Phase 1 (issue #3)

- What is the **IDOM / ODUR** layer, and what is its licence? Marked "to confirm" in the glossary.
- Is **Encuesta Multipropósito 2021** needed for Phase 3? It isn't in `sources.yaml` yet.
- What does **UTIEM** stand for? Marked "to confirm" in the glossary.
- Which **building-permit dataset**: the SDP layer, the curadurías register, or both? Both are in `sources.yaml` for now (issue #2).
- How many census blocks are anonymised, and is the 2018 cadastre downloadable?

## Gotchas from Phase 0

- **The shell is zsh:** a command stored in a variable (`$S args`) isn't split into words. Use a shell function instead.
- **macOS `sed` has no `\b`:** use `perl -pi -e` for word-boundary replacements.
- **DuckDB 2.0:** relations have no `.fetchone()`. Use `con.execute(sql).fetchone()`.
- **Snakemake 9 compares file content:** a changed timestamp alone doesn't trigger a re-run. It watches the commands in the Snakefile, not the package code, so stage sources are listed as inputs via `code()`.
- **`import tobler` takes about 14 s.** Keep heavy imports inside command bodies; a test enforces this for `--help`.
- **Local uv is 0.5.4** (old, but it works); the lock-file hook uses 0.13.8. `brew upgrade uv` is suggested.
- **`uvx <new tool>` was blocked** by the permission check (for example `cffconvert`). Ask Gregorio to run such tools.
- **Files over 1 MB are blocked** by pre-commit, and `data/` is git-ignored. Small fixtures go in `tests/fixtures/`.

## Suggested first message for the new session

> Read docs/session-handoff.md. We're starting Phase 1, issue #1, first checklist item (shared ingest machinery). Propose the design before writing code.
