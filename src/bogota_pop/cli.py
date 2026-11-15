"""Command-line entry point: ``bogota-pop``.

Each command maps to one pipeline stage. Keep heavy imports (geopandas, duckdb,
tobler) inside the command bodies so ``bogota-pop --help`` stays fast (ADR-0009).
"""

import logging
from pathlib import Path
from typing import Annotated

import typer

from bogota_pop import __version__

app = typer.Typer(
    name="bogota-pop",
    help="Open, reproducible population estimates for Bogotá D.C.",
    no_args_is_help=True,
    add_completion=False,
)


def _not_implemented(stage: str, phase: int) -> None:
    typer.echo(f"bogota-pop {stage}: not implemented yet (planned for Phase {phase}).", err=True)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"bogota-pop {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
) -> None:
    """Open, reproducible population estimates for Bogotá D.C."""


@app.command()
def ingest(
    source_ids: Annotated[
        list[str] | None,
        typer.Argument(help="Sources to ingest. Default: every source with a download_url."),
    ] = None,
    strict: Annotated[
        bool, typer.Option(help="Fail on sources with no pinned sha256 (ADR-0012).")
    ] = False,
    force: Annotated[
        bool, typer.Option(help="Download again even if a matching copy is already there.")
    ] = False,
    sources_yaml: Annotated[Path, typer.Option(hidden=True)] = Path("config/sources.yaml"),
    data_dir: Annotated[Path, typer.Option(hidden=True)] = Path("data"),
    manifest_json: Annotated[Path, typer.Option(hidden=True)] = Path("config/manifest.json"),
) -> None:
    """Download sources, verify checksums, write data/raw and data/interim."""
    from bogota_pop.ingest.core import ingest_source
    from bogota_pop.ingest.errors import IngestError
    from bogota_pop.ingest.sources import get_source, load_sources

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    sources = load_sources(sources_yaml)
    try:
        if source_ids:
            selected = [get_source(s, sources) for s in source_ids]
        else:
            selected = [s for s in sources.values() if s.download_url]
        if not selected:
            typer.echo("bogota-pop ingest: no source has a download_url yet.", err=True)
            return
        for source in selected:
            ingest_source(
                source,
                data_dir=data_dir,
                manifest_path=manifest_json,
                strict=strict,
                force=force,
            )
    except IngestError as err:
        typer.echo(f"bogota-pop ingest: {err}", err=True)
        raise typer.Exit(1) from None


@app.command("model")
def model_cmd() -> None:
    """Run the population estimate per lot."""
    _not_implemented("model", 2)


@app.command()
def validate() -> None:
    """Back-cast and survey checks; write the validation scorecard."""
    _not_implemented("validate", 4)


@app.command()
def publish() -> None:
    """Aggregate to block and H3, apply privacy rules, write release files."""
    _not_implemented("publish", 6)
