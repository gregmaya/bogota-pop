# ADR-0003: Main language: Python

- **Status:** Accepted
- **Date:** 2026-11-14
- **Plan reference:** D3 in [docs/plan.md](../plan.md)

## Context

The pipeline joins about 3 million cadastral predios to tens of thousands of census blocks, does areal interpolation and writes GeoParquet. It must run on a laptop and in CI, and be approachable for contributors from urban analytics and GIS.

## Decision

The pipeline is written in Python, using geopandas / shapely 2 / pyogrio for geometry, DuckDB with the spatial extension for heavy joins and aggregation, and tobler (PySAL) as the reference dasymetric implementation.

## Alternatives considered

- **R (sf, terra)** — strong spatial ecosystem, but a second language for CI, packaging and the later loader used by other Python projects.
- **PostGIS-centred pipeline** — powerful, but needs a database server, which raises the bar for "clone and run".
- **Mixed Python + R** — best-of-both for individual tasks, but doubles environment and CI maintenance.

## Consequences

- One environment, one test runner, one package; the `bogota_pop.load()` loader (Phase 6) is native for downstream Python users.
- GDAL/PROJ must install reliably on macOS and Linux CI; the environment tool is chosen with that in mind.
- R-only methods, if needed later, are ported or called out-of-process, not added as a core dependency.
