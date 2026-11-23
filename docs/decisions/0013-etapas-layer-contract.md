# ADR-0013: Etapas layer contract between the model and the viewer

- **Status:** Proposed
- **Date:** 2026-11-17
- **Plan reference:** "Etapas mode: every stage on the map" in [docs/plan.md](../plan.md)

## Context

Every stage of the pipeline should be looked at on a map before it is trusted: the census blocks as downloaded, the cadastral lots, the block matching, the model's estimates. The plan calls this the viewer's "Etapas" mode.

The viewer is a separate repo (`gregmaya/bogota-pop-viewer`) that only reads files this repo publishes. If each new layer needed new code in the viewer, the two repos would keep waiting on each other. We want to add a layer here and see it in the viewer without touching the viewer.

Two rules from earlier ADRs apply. Lot-level layers never leave the machine (ADR-0006). Published files have stable names and schemas, and changing them is a breaking change (CLAUDE.md, "Companion repo").

## Decision

**One list of layers, kept in this repo, is the only thing the two repos share.**

Think of it as a menu. The kitchen (this repo) writes the menu and cooks the dishes. The dining room (the viewer) shows whatever the menu lists, without knowing how anything was cooked. A new dish needs a new menu line, not a new dining room.

1. **`config/etapas.yaml`** lists every layer. A person edits it. Each entry says:

   | Key | What it is | Example |
   | --- | --- | --- |
   | `id` | Stable name, snake_case; also the file name | `mgn_2018_manzanas` |
   | `title` | Name shown in the viewer, in Spanish (ADR V4 in the viewer) | `Manzanas CNPV 2018` |
   | `review` | What to look for, in Spanish; shown next to the layer | `¿Coinciden con el mapa base?` |
   | `stage` | Pipeline stage that makes it | `ingest` |
   | `sources` | Source ids in `sources.yaml` it comes from | `[dane_mgn_cnpv2018_manzana]` |
   | `input` | The stage output it is drawn from | `data/interim/dane_mgn_cnpv2018_manzana/2018.parquet` |
   | `level` | `clase`, `upz`, `upl`, `manzana`, `h3`, `lote` or `construccion` | `manzana` |
   | `public` | May it go into a pre-release? | `true` |
   | `fields` | Columns kept in the tiles; everything else is dropped | `[COD_DANE_A, TP27_PERSO, TVIVIENDA]` |
   | `style` | A hint, not a full style: `{field, kind}` with `kind` one of `sequential`, `categorical`, `outline` | `{field: TP27_PERSO, kind: sequential}` |
   | `minzoom`, `maxzoom` | Zoom range of the tiles | `10`, `16` |

2. **The pipeline writes one PMTiles file per layer**, plus **`etapas.json`**, into `data/processed/etapas/`. `etapas.json` is what the viewer reads. It repeats each layer's entry and adds:
   - the file name
   - the field types
   - the bounds
   - the vigencia of each source
   - the attribution text, taken from each source's licence in `sources.yaml`
   - `schema_version`, the date it was made and the git commit of the model

3. **The viewer draws every layer the same generic way**, from `etapas.json` alone, using the `style` hint. Adding a layer here needs no code in the viewer. A new `style.kind` does need viewer code, so new kinds are agreed in both repos first.

4. **Privacy is checked in code, not by memory.** A layer at `lote` or `construccion` level must have `public: false`, and the pipeline stops if it doesn't. A `dev-YYYY-MM-DD` pre-release gets only the public layers, with an `etapas.json` that lists only those. The full `etapas.json` with private layers stays in `data/processed/etapas/`, and the viewer reads it there in local dev mode only.

5. **Tiles are written with GDAL's PMTiles driver** through pyogrio, which is already installed. Tiles must be in web map coordinates (EPSG:3857), so the reprojection happens here, when writing a publication file. Rule 4 in CLAUDE.md (everything internal in EPSG:9377) still holds for every internal file.

6. **`etapas.json` has a `schema_version`.** Adding an optional key is not breaking. Renaming or removing a key, or changing its meaning, raises the version and gets a changelog note, the same as any other published file.

## Alternatives considered

- **The layer list lives in the viewer.** The viewer would have to know paths and fields of the model's files, and each new stage would need a change in both repos. Rejected: the model repo knows its outputs; the viewer should not.
- **Hand-written styles per layer in the viewer.** Prettier per layer, but every layer becomes viewer work and the two repos move in lockstep. The `style` hint covers review needs; the public map (v0.1) can still have a hand-tuned style.
- **tippecanoe for tiles.** It makes very good tiles, but it is a system tool outside uv, and CLAUDE.md asks not to add system dependencies without asking. GDAL's driver is enough for review layers. If the public v0.1 tiles need better simplification, revisit for Phase 6 in a new ADR.
- **Review in QGIS only.** Works now that QGIS reads GeoParquet, but it can't be shared, and it does nothing for the viewer. QGIS stays the quick check for a single file.

## Consequences

- Each stage gets a review layer by adding a few lines to `etapas.yaml`. The checks on arrival become the `review` text, so they live with the layer, not in chat.
- The viewer can start now with a generic Etapas mode and a fixture `etapas.json`, without waiting for real layers.
- Follow-up here: a PMTiles writer in `publish`, a Snakemake rule per layer, a test for the privacy check, and the first layers (MGN blocks, MGN clase, UAECD blocks).
- Follow-up in the viewer: an ADR on how it reads `etapas.json` in release mode and in local mode.
- The plan's Etapas table becomes a summary; `config/etapas.yaml` is the real list.
