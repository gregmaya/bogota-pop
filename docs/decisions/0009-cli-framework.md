# ADR-0009: CLI framework: Typer

- **Status:** Accepted
- **Date:** 2026-11-14
- **Plan reference:** Phase 0, "CLI entry point" in [docs/plan.md](../plan.md)

## Context

The pipeline is driven through one command, `bogota-pop`, with subcommands per stage (`ingest`, `model`, `validate`, `publish`). Options will grow over time: a vigencia, a one-UPZ sample for CI, later a scenario file. The CLI is the first thing a new contributor touches.

## Decision

The CLI is built with Typer. Each subcommand is a type-hinted function; Typer derives the options and `--help` from the signature and docstring.

## Alternatives considered

- **argparse** — no dependency, but the most code per command, and options are declared separately from the function they feed.
- **Click** — mature and explicit, but options are declared twice (decorator and signature). Typer is built on Click, so Click remains available if ever needed.

## Consequences

- Adds `typer` (and with it `click`, `rich`, `shellingham`) as runtime dependencies.
- CLI tests use Typer's `CliRunner` instead of spawning subprocesses.
- Heavy libraries (tobler, geopandas, duckdb) are imported inside commands, not at module level, so `bogota-pop --help` stays fast.
