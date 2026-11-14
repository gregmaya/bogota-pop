# ADR-0001: Code licence: MIT

- **Status:** Accepted
- **Date:** 2026-11-14
- **Plan reference:** D1 in [docs/plan.md](../plan.md)

## Context

The pipeline is meant to be reused by public-sector bodies in Bogotá (SDP, UAECD), consultancies doing client work, and other researchers adapting the method to other cities. Any licence condition that needs legal review before adoption slows that reuse down, and public agencies are often the slowest to clear copyleft terms.

## Decision

All source code in this repository is released under the MIT licence (`LICENSE`).

## Alternatives considered

- **Apache 2.0** — adds an explicit patent grant, which matters little for an analysis pipeline, at the cost of a longer licence and NOTICE-file obligations.
- **GPL-3.0 / AGPL** — would force derived pipelines to stay open, but deters exactly the public-sector and client reuse the project wants.

## Consequences

- Anyone can reuse, modify and embed the code, including in closed work, with attribution.
- The code licence is separate from the data licence (ADR-0002); the two files must not be confused.
- Third-party code copied into the repo must be MIT-compatible.
