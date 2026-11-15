# ADR-0011: Issues, pull requests, milestones and releases in English and Spanish

- **Status:** Accepted
- **Date:** 2026-11-14
- **Plan reference:** D4 in [docs/plan.md](../plan.md); partly supersedes [ADR-0004](0004-repo-language.md)

## Context

ADR-0004 kept issues and pull requests in English only. The repo is public and the GitHub pages (issues, milestones, releases) are where most people will meet the project, including staff at the Secretaría Distrital de Planeación (SDP) and the Unidad Administrativa Especial de Catastro Distrital (UAECD) and local researchers who read Spanish first. Issues also tend to be read one at a time, out of context, so bare acronyms make them hard to follow.

## Decision

- Everything people read on GitHub is written in **English and Spanish**: issue and pull-request titles and bodies, milestones, labels, release notes, and the issue and PR templates.
- Titles use `English · Español`. Bodies have an English section followed by a Spanish section with the same content.
- Acronyms are spelled out the first time they appear in each issue, PR or release note, with the short form in brackets, e.g. "Unidad de Planeamiento Zonal (UPZ)". Expansions come from [docs/glossary.md](../glossary.md); an acronym whose expansion is not confirmed is marked as such, not guessed.
- Unchanged from ADR-0004: code, comments, commit messages and ADRs stay in English; README and methods pages are bilingual.

## Alternatives considered

- **Keep ADR-0004 (English only)** — less writing, but excludes the main local audience from the project's working space.
- **Spanish only on GitHub** — reaches local users, but cuts off the methods literature and international contributors.
- **Bilingual for the planning backlog only** — a mixed backlog (some issues bilingual, some not) is harder to read than either rule.

## Consequences

- Every issue and PR takes longer to write; templates carry both languages so the structure is already there.
- The glossary must be kept current: a new acronym in an issue means a new glossary row.
- ADR-0004 is marked as partly superseded (issues and PRs).
