from __future__ import annotations

from pathlib import Path

import click

from .config import load_config
from .loader import load_entries
from .portal import Portal
from .runlog import RunLog


@click.command()
@click.option(
    "--config",
    "config_path",
    default="config.yaml",
    show_default=True,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Pfad zur config.yaml",
)
@click.option(
    "--dry-run/--no-dry-run",
    default=True,
    show_default=True,
    help="Formular ausfüllen, aber nicht absenden",
)
@click.option(
    "--once",
    is_flag=True,
    help="Nur den ersten Eintrag aus der CSV abarbeiten (für Tests)",
)
@click.option(
    "--headed",
    is_flag=True,
    help="Browser sichtbar starten (statt headless)",
)
def main(config_path: Path, dry_run: bool, once: bool, headed: bool) -> None:
    """Halbjährliche PKN-Punkte-Einreichung."""
    config = load_config(config_path)
    runlog = RunLog(config.paths.log_file)
    entries = load_entries(config.paths.input_csv)

    if once:
        entries = entries[:1]

    click.echo(f"Modus: {'DRY-RUN' if dry_run else 'LIVE'}  |  Einträge: {len(entries)}")
    runlog.write("run.start", dry_run=dry_run, headed=headed, count=len(entries))

    with Portal(config, runlog, headless=not headed) as portal:
        portal.login()
        for i, entry in enumerate(entries, start=1):
            click.echo(f"[{i}/{len(entries)}] {entry.name} — {entry.session_date}")
            portal.submit_entry(entry, dry_run=dry_run)

    runlog.write("run.ok")
    click.echo("Fertig.")


if __name__ == "__main__":
    main()
