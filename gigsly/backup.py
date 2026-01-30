"""Backup and restore functionality for Gigsly."""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal, Optional

from gigsly.config import BACKUPS_DIR
from gigsly.db.crud import (
    create_contact_log,
    create_recurring_gig,
    create_show,
    create_venue,
    get_all_venues,
)
from gigsly.db.models import ContactLog, RecurringGig, Show, Venue
from gigsly.db.session import get_session

BACKUP_VERSION = 1


def _serialize_date(d: Optional[date]) -> Optional[str]:
    """Serialize date to ISO format string."""
    return d.isoformat() if d else None


def _serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Serialize datetime to ISO format string."""
    return dt.isoformat() if dt else None


def _deserialize_date(s: Optional[str]) -> Optional[date]:
    """Deserialize ISO format string to date."""
    return date.fromisoformat(s) if s else None


def _deserialize_datetime(s: Optional[str]) -> Optional[datetime]:
    """Deserialize ISO format string to datetime."""
    return datetime.fromisoformat(s) if s else None


def _venue_to_dict(venue: Venue) -> dict[str, Any]:
    """Convert venue to dictionary."""
    return {
        "id": venue.id,
        "name": venue.name,
        "location": venue.location,
        "address": venue.address,
        "contact_name": venue.contact_name,
        "contact_email": venue.contact_email,
        "contact_phone": venue.contact_phone,
        "mileage_one_way": venue.mileage_one_way,
        "typical_pay": venue.typical_pay,
        "payment_method": venue.payment_method,
        "requires_invoice": venue.requires_invoice,
        "has_w9": venue.has_w9,
        "booking_window_start": venue.booking_window_start,
        "booking_window_end": venue.booking_window_end,
        "notes": venue.notes,
        "created_at": _serialize_datetime(venue.created_at),
        "updated_at": _serialize_datetime(venue.updated_at),
    }


def _show_to_dict(show: Show) -> dict[str, Any]:
    """Convert show to dictionary."""
    return {
        "id": show.id,
        "venue_id": show.venue_id,
        "recurring_gig_id": show.recurring_gig_id,
        "venue_name_snapshot": show.venue_name_snapshot,
        "date": _serialize_date(show.date),
        "pay_amount": show.pay_amount,
        "payment_status": show.payment_status,
        "payment_received_date": _serialize_date(show.payment_received_date),
        "invoice_sent": show.invoice_sent,
        "invoice_sent_date": _serialize_date(show.invoice_sent_date),
        "is_cancelled": show.is_cancelled,
        "notes": show.notes,
        "created_at": _serialize_datetime(show.created_at),
        "updated_at": _serialize_datetime(show.updated_at),
    }


def _recurring_gig_to_dict(gig: RecurringGig) -> dict[str, Any]:
    """Convert recurring gig to dictionary."""
    return {
        "id": gig.id,
        "venue_id": gig.venue_id,
        "pay_amount": gig.pay_amount,
        "pattern_type": gig.pattern_type,
        "day_of_week": gig.day_of_week,
        "day_of_month": gig.day_of_month,
        "ordinal": gig.ordinal,
        "interval_weeks": gig.interval_weeks,
        "start_date": _serialize_date(gig.start_date),
        "end_date": _serialize_date(gig.end_date),
        "is_active": gig.is_active,
        "created_at": _serialize_datetime(gig.created_at),
        "updated_at": _serialize_datetime(gig.updated_at),
    }


def _contact_log_to_dict(log: ContactLog) -> dict[str, Any]:
    """Convert contact log to dictionary."""
    return {
        "id": log.id,
        "venue_id": log.venue_id,
        "contacted_at": _serialize_datetime(log.contacted_at),
        "method": log.method,
        "outcome": log.outcome,
        "follow_up_date": _serialize_date(log.follow_up_date),
        "notes": log.notes,
        "created_at": _serialize_datetime(log.created_at),
    }


def create_backup(output_path: Optional[str] = None, pretty: bool = False) -> Path:
    """
    Create a JSON backup of all data.

    Args:
        output_path: Optional output file path. Defaults to timestamped file in backups dir.
        pretty: If True, format JSON for human readability.

    Returns:
        Path to the created backup file.
    """
    if output_path:
        filepath = Path(output_path)
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        filepath = BACKUPS_DIR / f"backup-{timestamp}.json"

    with get_session() as session:
        venues = get_all_venues(session)

        data = {
            "version": BACKUP_VERSION,
            "created_at": datetime.now().isoformat(),
            "venues": [],
            "shows": [],
            "recurring_gigs": [],
            "contact_logs": [],
        }

        for venue in venues:
            data["venues"].append(_venue_to_dict(venue))
            for show in venue.shows:
                data["shows"].append(_show_to_dict(show))
            for gig in venue.recurring_gigs:
                data["recurring_gigs"].append(_recurring_gig_to_dict(gig))
            for log in venue.contact_logs:
                data["contact_logs"].append(_contact_log_to_dict(log))

    # Write to file
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        if pretty:
            json.dump(data, f, indent=2)
        else:
            json.dump(data, f)

    return filepath


def restore_backup(
    filepath: str, mode: Literal["replace", "merge"] = "replace"
) -> dict[str, int]:
    """
    Restore data from a JSON backup file.

    Args:
        filepath: Path to the backup file.
        mode: "replace" wipes existing data, "merge" combines with existing.

    Returns:
        Stats about what was restored.
    """
    with open(filepath) as f:
        data = json.load(f)

    stats = {"venues": 0, "shows": 0, "recurring_gigs": 0, "contact_logs": 0}

    with get_session() as session:
        if mode == "replace":
            # Clear existing data
            from gigsly.db.models import Base

            for table in reversed(Base.metadata.sorted_tables):
                session.execute(table.delete())

        # Track ID mappings for merge mode
        venue_id_map: dict[int, int] = {}

        # Restore venues
        existing_venue_names = set()
        if mode == "merge":
            for v in get_all_venues(session):
                existing_venue_names.add(v.name.lower())

        for venue_data in data.get("venues", []):
            old_id = venue_data.pop("id")
            venue_data.pop("created_at", None)
            venue_data.pop("updated_at", None)

            if mode == "merge" and venue_data["name"].lower() in existing_venue_names:
                # Skip duplicate venues in merge mode
                continue

            venue = create_venue(session, **venue_data)
            venue_id_map[old_id] = venue.id
            stats["venues"] += 1

        # Restore recurring gigs
        for gig_data in data.get("recurring_gigs", []):
            old_venue_id = gig_data.pop("venue_id")
            gig_data.pop("id")
            gig_data.pop("created_at", None)
            gig_data.pop("updated_at", None)

            new_venue_id = venue_id_map.get(old_venue_id)
            if new_venue_id is None:
                continue

            gig_data["venue_id"] = new_venue_id
            gig_data["start_date"] = _deserialize_date(gig_data["start_date"])
            gig_data["end_date"] = _deserialize_date(gig_data.get("end_date"))

            create_recurring_gig(session, **gig_data)
            stats["recurring_gigs"] += 1

        # Restore shows
        for show_data in data.get("shows", []):
            old_venue_id = show_data.pop("venue_id", None)
            show_data.pop("id")
            show_data.pop("recurring_gig_id", None)  # Don't restore this relationship
            show_data.pop("created_at", None)
            show_data.pop("updated_at", None)

            if old_venue_id:
                new_venue_id = venue_id_map.get(old_venue_id)
                if new_venue_id is None:
                    continue
                show_data["venue_id"] = new_venue_id

            show_data["date"] = _deserialize_date(show_data["date"])
            show_data["payment_received_date"] = _deserialize_date(
                show_data.get("payment_received_date")
            )
            show_data["invoice_sent_date"] = _deserialize_date(
                show_data.get("invoice_sent_date")
            )

            create_show(session, **show_data)
            stats["shows"] += 1

        # Restore contact logs
        for log_data in data.get("contact_logs", []):
            old_venue_id = log_data.pop("venue_id")
            log_data.pop("id")
            log_data.pop("created_at", None)

            new_venue_id = venue_id_map.get(old_venue_id)
            if new_venue_id is None:
                continue

            log_data["venue_id"] = new_venue_id
            log_data["contacted_at"] = _deserialize_datetime(log_data["contacted_at"])
            log_data["follow_up_date"] = _deserialize_date(log_data.get("follow_up_date"))

            create_contact_log(session, **log_data)
            stats["contact_logs"] += 1

    return stats
