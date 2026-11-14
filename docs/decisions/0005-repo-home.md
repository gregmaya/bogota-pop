# ADR-0005: Repo home: personal GitHub account

- **Status:** Accepted
- **Date:** 2026-11-14
- **Plan reference:** D5 in [docs/plan.md](../plan.md)

## Context

The project starts as a single-maintainer effort. An organisation adds setup and governance overhead before there is anyone else to govern with.

## Decision

The repository lives under the personal GitHub account `gregmaya`, public from the first commit.

## Alternatives considered

- **New GitHub organisation now** — better long-term branding and shared ownership, but premature with one maintainer.
- **An existing institutional organisation** — would tie the project to one institution's policies before it has proved its value.

## Consequences

- GitHub redirects repository URLs after a transfer, so moving to an organisation later is cheap.
- The Zenodo integration (ADR-0007) must be re-linked if the repo is transferred; existing DOIs stay valid.
- GitHub Pages URLs (methods site, viewer) would change on transfer and need a redirect note.
