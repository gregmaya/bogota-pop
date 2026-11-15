# ADR-0010: Orchestration: Snakemake

- **Status:** Accepted
- **Date:** 2026-11-14
- **Plan reference:** Phase 0 exit gate and "Orchestration" in the stack table, [docs/plan.md](../plan.md)

## Context

The pipeline is a chain of stages (ingest → model → validate → publish), each reading the files the previous one wrote. The plan requires that a single command rebuilds everything from raw downloads, that only stages whose inputs changed re-run, and that a new release is "the same pipeline for another vigencia" with no code edits (Phase 3 exit gate). Running stages by hand and remembering what a change affects does not meet that.

## Decision

The pipeline DAG lives in `pipeline/Snakefile` and runs with Snakemake (9.x):

```bash
uv run snakemake -s pipeline/Snakefile -c1                        # build
uv run snakemake -s pipeline/Snakefile -n                         # dry run
uv run snakemake -s pipeline/Snakefile -c1 --config vigencia=2027 # another vigencia
```

- Each rule calls one `bogota-pop` command; the CLI (ADR-0009) stays the single entry point and holds the logic. The Snakefile holds only the wiring: inputs, outputs, logs.
- Outputs are parameterised by `{vigencia}`.
- Each rule lists its stage's source files (`src/bogota_pop/<stage>/`) and the CLI as inputs, so editing a stage's code re-runs that stage and everything downstream.
- Each rule writes a log to `data/logs/{vigencia}/<stage>.log`.

## Alternatives considered

- **Make** — pre-installed and simple, but decides what to re-run from file timestamps only, handles "same rule for another year" awkwardly, and adds a second syntax with its own pitfalls (tabs) to a Python-only project (ADR-0003).
- **No orchestrator (CLI runs stages in order)** — fewer tools, but every stage would re-run every time, or the project would end up re-implementing dependency tracking.
- **Heavier workflow engines (Prefect, Dagster, Airflow)** — built for scheduled production services with servers and UIs; far more than a laptop-scale research pipeline needs.

## Consequences

- Snakemake re-runs a rule when an input's content changes, when the rule's own command changes, or when a listed source file changes. A changed timestamp with identical content does not trigger a re-run.
- Adds `snakemake` as a runtime dependency (about 35 packages with its own dependencies). If the Phase 6 loader (`bogota_pop.load()`) should install lighter, Snakemake can move to an optional extra then.
- Snakemake's per-rule conda/container environments are not used: uv provides one environment for the whole project.
- Phase 0 rules write marker files (`.ingest.done`, …) because the stages are stubs. From Phase 1 each rule's outputs become the real files (GeoParquet, PMTiles, scorecard), and each `bogota-pop` command gains the arguments it needs (`--vigencia`, paths).
- CI runs the pipeline end to end on every push.
