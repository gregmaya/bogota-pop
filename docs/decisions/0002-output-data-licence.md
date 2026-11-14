# ADR-0002: Output data licence: CC BY 4.0

- **Status:** Accepted
- **Date:** 2026-11-14
- **Plan reference:** D2 in [docs/plan.md](../plan.md)

## Context

Published outputs (block and H3 population estimates) are derived from DANE census data, UAECD cadastre and SDP projections. Datos Abiertos Bogotá and DANE publish under attribution-style terms. The output licence has to be compatible with those inputs and keep the attribution chain clear for anyone who reuses the estimates.

## Decision

All published data outputs are released under Creative Commons Attribution 4.0 International (CC BY 4.0), stated in `DATA_LICENSE`. Each release credits the upstream sources it was built from.

## Alternatives considered

- **CC0** — simplest for users, but drops the attribution that upstream terms expect us to pass on.
- **ODbL** — share-alike would complicate reuse in client and government work and does not match upstream terms.

## Consequences

- Users may reuse and redistribute outputs for any purpose, with attribution to this project and its sources.
- Each release needs a citation (`CITATION.cff`, Zenodo DOI per ADR-0007) and a source list.
- If an input's licence turns out to be stricter (for example CNPV microdata terms, checked in Phase 1), outputs derived from it must be reviewed before release.
