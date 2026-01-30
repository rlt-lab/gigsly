"""CLI entry points for Gigsly."""

from datetime import date

import click

from gigsly.config import BACKUPS_DIR, ensure_gigsly_dir
from gigsly.db.session import init_db


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Gigsly - Track gigs, venues, payments, and booking outreach."""
    ensure_gigsly_dir()
    init_db()

    if ctx.invoked_subcommand is None:
        # Launch TUI when no subcommand given
        from gigsly.app import run_app

        run_app()


@main.command()
def report():
    """Display smart report in terminal."""
    from gigsly.reports import print_smart_report

    print_smart_report()


@main.command()
@click.argument("year", type=int, default=None, required=False)
def tax(year):
    """Display tax report for a given year.

    If no year is provided, defaults to current year.
    """
    if year is None:
        year = date.today().year

    from gigsly.reports import print_tax_report

    print_tax_report(year)


@main.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path. Defaults to ~/.gigsly/backups/backup-YYYY-MM-DD.json",
)
def backup(output):
    """Export all data to JSON backup file."""
    from gigsly.backup import create_backup

    filepath = create_backup(output)
    click.echo(f"Backup created: {filepath}")


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option(
    "--merge",
    is_flag=True,
    help="Merge with existing data instead of replacing",
)
def restore(filepath, merge):
    """Restore data from JSON backup file.

    Default mode replaces all existing data.
    Use --merge to combine with existing data.
    """
    from gigsly.backup import restore_backup

    mode = "merge" if merge else "replace"
    stats = restore_backup(filepath, mode=mode)
    click.echo(f"Restored: {stats['venues']} venues, {stats['shows']} shows")


@main.command("export-calendar")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="gigsly-calendar.ics",
    help="Output ICS file path",
)
@click.option(
    "--future-only",
    is_flag=True,
    help="Only export future shows",
)
def export_calendar(output, future_only):
    """Export shows to ICS calendar file."""
    from gigsly.ics_export import export_to_ics

    count = export_to_ics(output, future_only=future_only)
    click.echo(f"Exported {count} shows to {output}")


@main.command("import-calendar")
@click.argument("filepath", type=click.Path(exists=True))
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview what would be imported without making changes",
)
def import_calendar(filepath, dry_run):
    """Import events from ICS calendar file."""
    from gigsly.ics_export import import_from_ics

    stats = import_from_ics(filepath, dry_run=dry_run)
    if dry_run:
        click.echo("Dry run - no changes made:")
    click.echo(f"Shows: {stats['shows_created']} created, {stats['shows_skipped']} skipped")
    if stats.get("venues_created", 0):
        click.echo(f"Venues: {stats['venues_created']} created")


@main.command("export-json")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="gigsly-export.json",
    help="Output JSON file path",
)
def export_json(output):
    """Export all data to JSON file (human-readable format)."""
    from gigsly.backup import create_backup

    filepath = create_backup(output, pretty=True)
    click.echo(f"Exported to {filepath}")


if __name__ == "__main__":
    main()
