# ADR-0006: Public granularity: block and H3 public; lot level private

- **Status:** Accepted
- **Date:** 2026-11-14
- **Plan reference:** D6 in [docs/plan.md](../plan.md)

## Context

The model estimates population per cadastral lot. In single-family lots a modelled count is close to revealing a household's size. DANE itself suppresses census counts for blocks with 1–3 dwellings (the `DATO_ANM` flag) for this reason.

## Decision

- Public outputs are published only at block (manzana) and H3 level.
- Lot-level estimates are computed and used internally but never published, committed, or uploaded to releases or public tiles.
- Before export, aggregates with fewer than a threshold of dwellings are suppressed or merged, mirroring DANE's 1–3 dwelling rule, and counts are rounded (rules set in Phase 6).

## Alternatives considered

- **Publish lot level** — most useful for some analyses, but creates disclosure risk the official statistics office already avoids.
- **Publish only UPZ / UPL** — safest, but too coarse for the planning uses that motivate the project.

## Consequences

- `publish/` must enforce the privacy rules; tests check that no lot-level geometry or ID appears in public artefacts.
- Lot-level stage layers in the viewer's Etapas mode are local-only.
- The H3 resolution (9 vs 10) is chosen in Phase 6 partly on disclosure risk.
