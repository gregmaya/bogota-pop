# ADR-0008: Control total: DANE–SDP post-COVID projections (2025 release)

- **Status:** Accepted
- **Date:** 2026-11-14
- **Plan reference:** D8 in [docs/plan.md](../plan.md)

## Context

Lot estimates are raked so they sum to an official total per UPZ / UPL. Candidate totals disagree: the DANE–SDP projections give about 7.9 M for 2024, while the Encuesta de Movilidad 2023 expands to about 7.5 M. Using different totals in different places would make results impossible to compare and invite disputes.

## Decision

The single control total is the DANE–SDP post-COVID population projections, 2025 release, by UPZ / UPL and year. Each output records the control year and the projection release it used.

## Alternatives considered

- **CNPV 2018 adjusted for omission** — official, but frozen in 2018.
- **Encuesta de Movilidad 2023 total** — independent, but a survey expansion with a different total; used for validation (shares, not counts) instead.
- **Encuesta Multipropósito 2025** — kept as an independent validation source, not a control.

## Consequences

- UPZ / UPL totals match the official projection exactly by construction; validation must use independent sources (the Phase 4 scorecard).
- When DANE–SDP revise projections, an interim release is cut and the change is recorded in `CHANGELOG.md`.
- The documented gap with the Movilidad total is stated in the methods page.
