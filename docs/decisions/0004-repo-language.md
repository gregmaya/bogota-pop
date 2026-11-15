# ADR-0004: Repo language: English code and issues; bilingual README and methods

- **Status:** Accepted; partly superseded by [ADR-0011](0011-bilingual-github.md) (issues and PRs are now bilingual)
- **Date:** 2026-11-14
- **Plan reference:** D4 in [docs/plan.md](../plan.md)

## Context

Two audiences matter. Spanish-speaking users (SDP, UAECD, Bogotá academia) are the main consumers of the data. The dasymetric and population-modelling literature, and most potential code contributors, work in English.

## Decision

- Code, comments, commit messages, issues, PRs and ADRs are in English.
- `README.md` / `README.es.md` and the methods site are maintained in both English and Spanish.
- Source field names (for example `STP27_PERS`, `DATO_ANM`) and official Spanish terms (manzana, vigencia, UPZ) keep their original form.

## Alternatives considered

- **Spanish only** — best for local users, but cuts off the international methods audience.
- **English only** — simplest, but makes the project hard to adopt locally, which is where it is most useful.

## Consequences

- Each docs change touching README or methods pages needs both languages updated; PR review checks this.
- The online viewer (separate repo) is Spanish only (viewer decision V4); that does not change this ADR.
