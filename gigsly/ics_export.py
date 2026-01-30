"""ICS calendar import/export for Gigsly."""

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from icalendar import Calendar, Event

from gigsly.db.crud import create_show, create_venue, get_all_shows, search_venues
from gigsly.db.session import get_session


def export_to_ics(output_path: str, future_only: bool = False) -> int:
    """
    Export shows to ICS calendar file.

    Args:
        output_path: Path for the output ICS file.
        future_only: If True, only export future shows.

    Returns:
        Number of shows exported.
    """
    cal = Calendar()
    cal.add("prodid", "-//Gigsly//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("x-wr-calname", "Gigsly Shows")

    count = 0

    with get_session() as session:
        shows = get_all_shows(session)

        for show in shows:
            if show.is_cancelled:
                continue

            if future_only and show.date < date.today():
                continue

            event = Event()

            # Summary: Venue name
            summary = show.display_name
            if show.pay_amount:
                summary += f" (${show.pay_amount:.0f})"
            event.add("summary", summary)

            # Date/time
            if show.start_time:
                dtstart = datetime.combine(show.date, show.start_time)
                event.add("dtstart", dtstart)
                if show.end_time:
                    dtend = datetime.combine(show.date, show.end_time)
                    event.add("dtend", dtend)
                else:
                    event.add("dtend", dtstart + timedelta(hours=2))
            else:
                event.add("dtstart", show.date)
                event.add("dtend", show.date)

            # Location
            if show.venue and show.venue.address:
                event.add("location", show.venue.address)

            # Description
            desc_parts = []
            if show.pay_amount:
                desc_parts.append(f"Pay: ${show.pay_amount:.2f}")
            if show.payment_status:
                desc_parts.append(f"Status: {show.payment_status}")
            if show.notes:
                desc_parts.append(f"Notes: {show.notes}")
            if desc_parts:
                event.add("description", "\n".join(desc_parts))

            # UID for tracking
            event.add("uid", f"gigsly-show-{show.id}@gigsly.local")

            cal.add_component(event)
            count += 1

    # Write to file
    with open(output_path, "wb") as f:
        f.write(cal.to_ical())

    return count


def import_from_ics(filepath: str, dry_run: bool = False) -> dict[str, int]:
    """
    Import events from ICS calendar file.

    Args:
        filepath: Path to the ICS file.
        dry_run: If True, don't actually create records.

    Returns:
        Stats about what was imported.
    """
    stats = {"shows_created": 0, "shows_skipped": 0, "venues_created": 0}

    with open(filepath, "rb") as f:
        cal = Calendar.from_ical(f.read())

    with get_session() as session:
        for component in cal.walk():
            if component.name != "VEVENT":
                continue

            # Extract event data
            summary = str(component.get("summary", ""))
            dtstart = component.get("dtstart")
            location = str(component.get("location", "")) if component.get("location") else None

            if not dtstart:
                stats["shows_skipped"] += 1
                continue

            # Get date from dtstart
            dt = dtstart.dt
            if isinstance(dt, datetime):
                show_date = dt.date()
                start_time = dt.time()
            else:
                show_date = dt
                start_time = None

            # Parse venue name from summary
            # Remove pay amount if present: "Venue Name ($200)" -> "Venue Name"
            venue_name = summary
            if "($" in venue_name:
                venue_name = venue_name.split("($")[0].strip()

            if not venue_name:
                stats["shows_skipped"] += 1
                continue

            if dry_run:
                stats["shows_created"] += 1
                continue

            # Find or create venue
            venues = search_venues(session, venue_name)
            if venues:
                # Case-insensitive match
                venue = next(
                    (v for v in venues if v.name.lower() == venue_name.lower()),
                    venues[0],
                )
            else:
                # Create minimal venue
                venue = create_venue(
                    session,
                    name=venue_name,
                    address=location,
                )
                stats["venues_created"] += 1

            # Create show
            create_show(
                session,
                venue_id=venue.id,
                date=show_date,
                start_time=start_time,
            )
            stats["shows_created"] += 1

    return stats
