# CLAUDE.md — bogota-pop

Open, reproducible model of resident population for Bogotá D.C. Population is estimated per cadastral lot, refreshed once per cadastral vigencia, and published at block (manzana) and H3 level.

The full plan lives in `docs/plan.md`. Decisions live in `docs/decisions/` as ADRs. Read both before starting a new phase or changing anything structural.

## Current status

- Phase: **0, Bootstrap** (update this line when a phase closes)
- Next release: `v0.1` (MVP census-to-lot model, Phase 2)

## Method in one paragraph

CNPV 2018 population per block (DANE MGN integrado) is distributed to cadastral lots (UAECD) using residential weight. PH lots use their count of residential units. NPH lots use residential built area. The result is then scaled so that every UPZ/UPL matches the DANE–SDP post-COVID projection for the target year. From v1.0 the model switches to the housing-unit method: units per lot × occupancy × persons per household, still controlled to the same projections.

## Stack

- Python only (ADR-0003). Environment managed with **uv**: `pyproject.toml` + `uv.lock`, both committed. Add dependencies with `uv add`, never with plain `pip install`. GDAL comes bundled in the pyogrio/shapely wheels; don't add a system GDAL dependency without asking.
- geopandas, shapely 2, pyogrio, DuckDB with the spatial extension, tobler, h3-py.
- Orchestration: Snakemake or Make (decide in Phase 0, then update this line).
- Quality: ruff, pytest, pre-commit, GitHub Actions.

## Commands

```bash
uv sync                       # create/refresh .venv from uv.lock
uv run bogota-pop ingest      # download sources, verify checksums, write data/raw and data/interim
uv run bogota-pop model       # run the population estimate
uv run bogota-pop validate    # back-cast and survey checks, write the scorecard
uv run bogota-pop publish     # aggregate to block/H3, apply privacy rules, write GeoParquet + PMTiles
uv run pytest                 # tests; the integration test runs on a single UPZ sample
uv run ruff check . && uv run ruff format .
```

Update this block when the real commands differ.

## Repository layout

- `config/sources.yaml`: every dataset with URL, vigencia, licence and checksum. A new source gets added here first.
- `config/model.yaml`: weights, thresholds, control year. No magic numbers in code.
- `src/bogota_pop/{ingest,harmonise,model,validate,publish}/`: one module per stage.
- `pipeline/`: the DAG. Stages only run through it or through the CLI.
- `notebooks/`: exploration only. Never a pipeline step, and nothing in `src/` imports from it.
- `docs/methods/`: methods site. `docs/decisions/`: ADRs.
- `data/`: git-ignored (`raw/`, `interim/`, `processed/`).

## Hard rules

1. **Never commit data.** Nothing under `data/` goes into git. Downloads are recorded in `manifest.json` (URL, vigencia, download date, SHA-256).
2. **Lot-level outputs stay private** (ADR-0006). Only block and H3 aggregates go into public releases, public tiles or the docs. A layer at lot level, such as residential weights or per-lot estimates, is local only. When unsure about a layer, treat it as private.
3. **One control total:** DANE–SDP post-COVID projections (ADR-0008). Don't mix in EM 2025 or Encuesta de Movilidad totals as controls; they are validation sources only.
4. **CRS:** everything internal is MAGNA-SIRGAS Origen Nacional, EPSG:9377. Reproject at ingest, never later.
5. **Format:** GeoParquet internally. GeoPackage and CSV only as publication extras.
6. **No invented numbers.** Every figure in the README, methods site or changelog is produced by code in the repo. If a number isn't computed yet, write a TODO, not an estimate.
7. **Match blocks by geometry, not by code.** MGN and UAECD block codes differ. Every unmatched block is logged.
8. **CI never downloads full datasets.** Tests use the small fixtures in `tests/fixtures/`.

## Conventions

- Code, comments, commit messages, issues and PRs in English. README and methods pages in English and Spanish (`README.md`, `README.es.md`).
- Keep original Spanish source field names where they come from (`STP27_PERS`, `DATO_ANM`, `CODMANPRE`). Map them to English snake_case names in one place in `harmonise/`, documented in the data dictionary.
- Type hints on public functions. Short docstrings that say what a function expects and returns, including CRS and units.
- Each pipeline stage writes, next to its output, a PMTiles file for the viewer's "Etapas" mode. Block and H3 stages may be published as dev pre-releases (`dev-YYYY-MM-DD`). Lot-level stage tiles stay in `data/processed/`.
- Releases are tagged by cadastral vigencia (`v2026.1`). Every release gets a `CHANGELOG.md` entry covering data, method and results.

## How to work with me (Greg)

- Talk a decision through before writing code for it. If something isn't covered by the plan or an ADR, propose it and wait.
- Stop after each step of a phase for review. Don't chain several steps in one go.
- A new structural decision becomes a new ADR (`docs/decisions/ADR-00NN-short-title.md`: context, decision, consequences).
- When scope or order changes, update `docs/plan.md` in the same PR.
- Prefer small PRs, one per task from the phase checklist.
- Prose in docs: direct, specific, varied sentence length, no filler intros or recap endings.

## Companion repo

The web viewer lives in `gregmaya/bogota-pop-viewer`. It only consumes files this repo publishes (PMTiles + UPZ/UPL summary JSON attached to Releases). Don't add viewer code here, and keep the published file names and schemas stable. Changing them is a breaking change and needs a note in the changelog.
