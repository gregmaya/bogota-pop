"""Command-line entry point: ``bogota-pop``.

Each command maps to one pipeline stage. Keep heavy imports (geopandas, duckdb,
tobler) inside the command bodies so ``bogota-pop --help`` stays fast (ADR-0009).
"""

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
def ingest() -> None:
    """Download sources, verify checksums, write data/raw and data/interim."""
    _not_implemented("ingest", 1)


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
