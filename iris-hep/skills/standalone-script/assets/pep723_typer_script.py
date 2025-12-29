#!/usr/bin/env -S uv run --script
# NOTE: Be careful editing this block; requires-python and dependencies control uv/PEP 723 execution.
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
# ]
# ///
import logging

import typer

app = typer.Typer(add_completion=False)


@app.command()
def main(verbose: int = typer.Option(0, "-v", "--verbose", count=True)) -> None:
    """Describe what the script does."""
    log_level = logging.WARNING
    if verbose == 1:
        log_level = logging.INFO
    elif verbose >= 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    typer.echo("Hello from Typer.")


if __name__ == "__main__":
    app()
