# Architecture Decision Records

One short file per decision, so readers can see *why* the project is built the way it is, not only *what* it does.

ADRs are immutable once accepted. To change a decision, write a new ADR that supersedes the old one and update the old one's status to `Superseded by ADR-XXXX`.

| ADR | Title | Status | Date |
| --- | --- | --- | --- |
| [0001](0001-code-licence.md) | Code licence: MIT | Accepted | 2026-11-14 |
| [0002](0002-output-data-licence.md) | Output data licence: CC BY 4.0 | Accepted | 2026-11-14 |
| [0003](0003-main-language.md) | Main language: Python | Accepted | 2026-11-14 |
| [0004](0004-repo-language.md) | Repo language: English code, bilingual docs | Partly superseded by 0011 | 2026-11-14 |
| [0005](0005-repo-home.md) | Repo home: personal GitHub account | Accepted | 2026-11-14 |
| [0006](0006-public-granularity.md) | Public granularity: block and H3; lot level private | Accepted | 2026-11-14 |
| [0007](0007-where-outputs-live.md) | Outputs on GitHub Releases, Zenodo DOI for majors | Accepted | 2026-11-14 |
| [0008](0008-control-total.md) | Control total: DANE–SDP post-COVID projections | Accepted | 2026-11-14 |
| [0009](0009-cli-framework.md) | CLI framework: Typer | Accepted | 2026-11-14 |
| [0010](0010-orchestration.md) | Orchestration: Snakemake | Accepted | 2026-11-14 |
| [0011](0011-bilingual-github.md) | Issues, PRs, milestones and releases in English and Spanish | Accepted | 2026-11-14 |
| [0012](0012-ingest-provenance.md) | Ingest provenance: checksums and manifest | Accepted | 2026-11-15 |

New ADRs copy [template.md](template.md) and take the next number.
