# bogota-pop

Open, reproducible population estimates for every cadastral lot in Bogotá D.C., published at block (manzana) and H3 level.

> Work in progress (Phase 0). See [docs/plan.md](docs/plan.md) and [docs/decisions/](docs/decisions/).

## Development setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/gregmaya/bogota-pop.git
cd bogota-pop
uv sync
uv run pre-commit install   # once per clone
uv run bogota-pop --help
uv run snakemake -s pipeline/Snakefile -c1   # run the (still empty) pipeline
```

Code: MIT ([LICENSE](LICENSE)). Data outputs: CC BY 4.0 ([DATA_LICENSE](DATA_LICENSE)). How to cite: [CITATION.cff](CITATION.cff).
