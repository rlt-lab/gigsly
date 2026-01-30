"""CRUD operations for Gigsly models."""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from gigsly.db.models import ContactLog, RecurringGig, Show, Venue


# ============================================================================
# Venue CRUD
# ============================================================================


def create_venue(session: Session, **kwargs) -> Venue:
    """Create a new venue."""
    venue = Venue(**kwargs)
    session.add(venue)
    session.flush()
    return venue


def get_venue(session: Session, venue_id: int) -> Optional[Venue]:
    """Get a venue by ID."""
    return session.get(Venue, venue_id)


def get_venue_with_relations(session: Session, venue_id: int) -> Optional[Venue]:
    """Get a venue with all related data eagerly loaded."""
    stmt = (
        select(Venue)
        .options(
            joinedload(Venue.shows),
            joinedload(Venue.recurring_gigs),
            joinedload(Venue.contact_logs),
        )
        .where(Venue.id == venue_id)
    )
    return session.scalars(stmt).unique().first()


def get_all_venues(session: Session) -> list[Venue]:
    """Get all venues."""
    stmt = select(Venue).order_by(Venue.name)
    return list(session.scalars(stmt))


def search_venues(session: Session, query: str) -> list[Venue]:
    """Search venues by name, location, or contact name."""
    q = f"%{query.lower()}%"
    stmt = (
        select(Venue)
        .where(
            (Venue.name.ilike(q))
            | (Venue.location.ilike(q))
            | (Venue.contact_name.ilike(q))
        )
        .order_by(Venue.name)
    )
    return list(session.scalars(stmt))


def update_venue(session: Session, venue_id: int, **kwargs) -> Optional[Venue]:
    """Update a venue."""
    venue = get_venue(session, venue_id)
    if venue:
        for key, value in kwargs.items():
            if hasattr(venue, key):
                setattr(venue, key, value)
        session.flush()
    return venue


def delete_venue(session: Session, venue_id: int) -> bool:
    """
    Delete a venue with proper handling of related data.

    - Past shows: Preserve with venue_name_snapshot
    - Future shows: Mark as cancelled
    - Recurring gigs: Deactivate
    - Contact logs: Preserved (orphaned)
    """
    venue = get_venue_with_relations(session, venue_id)
    if not venue:
        return False

    today = date.today()

    # Handle shows
    for show in venue.shows:
        if show.date < today:
            # Past show - preserve with snapshot
            show.venue_name_snapshot = venue.name
            show.venue_id = None
        else:
            # Future show - cancel
            show.is_cancelled = True

    # Deactivate recurring gigs
    for gig in venue.recurring_gigs:
        gig.is_active = False

    # Actually delete the venue
    session.delete(venue)
    session.flush()
    return True


# ============================================================================
# Show CRUD
# ============================================================================


def create_show(session: Session, **kwargs) -> Show:
    """Create a new show."""
    show = Show(**kwargs)
    session.add(show)
    session.flush()
    return show


def get_show(session: Session, show_id: int) -> Optional[Show]:
    """Get a show by ID."""
    return session.get(Show, show_id)


def get_show_with_venue(session: Session, show_id: int) -> Optional[Show]:
    """Get a show with venue eagerly loaded."""
    stmt = select(Show).options(joinedload(Show.venue)).where(Show.id == show_id)
    return session.scalars(stmt).first()


def get_all_shows(session: Session) -> list[Show]:
    """Get all shows, ordered by date descending."""
    stmt = select(Show).options(joinedload(Show.venue)).order_by(Show.date.desc())
    return list(session.scalars(stmt).unique())


def get_upcoming_shows(session: Session, limit: Optional[int] = None) -> list[Show]:
    """Get upcoming shows (today or later)."""
    stmt = (
        select(Show)
        .options(joinedload(Show.venue))
        .where(Show.date >= date.today(), Show.is_cancelled == False)
        .order_by(Show.date)
    )
    if limit:
        stmt = stmt.limit(limit)
    return list(session.scalars(stmt).unique())


def get_past_shows(session: Session) -> list[Show]:
    """Get past shows."""
    stmt = (
        select(Show)
        .options(joinedload(Show.venue))
        .where(Show.date < date.today())
        .order_by(Show.date.desc())
    )
    return list(session.scalars(stmt).unique())


def get_unpaid_shows(session: Session) -> list[Show]:
    """Get past unpaid shows."""
    stmt = (
        select(Show)
        .options(joinedload(Show.venue))
        .where(
            Show.date < date.today(),
            Show.payment_status == "pending",
            Show.is_cancelled == False,
        )
        .order_by(Show.date)
    )
    return list(session.scalars(stmt).unique())


def get_shows_needing_invoice(session: Session) -> list[Show]:
    """Get shows that need invoices sent."""
    stmt = (
        select(Show)
        .join(Venue)
        .options(joinedload(Show.venue))
        .where(
            Show.date < date.today(),
            Show.payment_status == "pending",
            Show.invoice_sent == False,
            Show.is_cancelled == False,
            Venue.requires_invoice == True,
        )
        .order_by(Show.date)
    )
    return list(session.scalars(stmt).unique())


def get_shows_for_venue(session: Session, venue_id: int) -> list[Show]:
    """Get all shows for a specific venue."""
    stmt = select(Show).where(Show.venue_id == venue_id).order_by(Show.date.desc())
    return list(session.scalars(stmt))


def get_shows_in_range(session: Session, start_date: date, end_date: date) -> list[Show]:
    """Get shows within a date range."""
    stmt = (
        select(Show)
        .options(joinedload(Show.venue))
        .where(Show.date >= start_date, Show.date <= end_date)
        .order_by(Show.date)
    )
    return list(session.scalars(stmt).unique())


def get_shows_for_year(session: Session, year: int) -> list[Show]:
    """Get all shows for a specific year (for tax reports)."""
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    return get_shows_in_range(session, start, end)


def get_show_for_recurring_date(
    session: Session, recurring_gig_id: int, show_date: date
) -> Optional[Show]:
    """Get a show for a specific recurring gig and date (for idempotent generation)."""
    stmt = select(Show).where(
        Show.recurring_gig_id == recurring_gig_id, Show.date == show_date
    )
    return session.scalars(stmt).first()


def update_show(session: Session, show_id: int, **kwargs) -> Optional[Show]:
    """Update a show."""
    show = get_show(session, show_id)
    if show:
        for key, value in kwargs.items():
            if hasattr(show, key):
                setattr(show, key, value)
        session.flush()
    return show


def mark_show_paid(session: Session, show_id: int, payment_date: date) -> Optional[Show]:
    """Mark a show as paid."""
    return update_show(
        session, show_id, payment_status="paid", payment_received_date=payment_date
    )


def mark_invoice_sent(session: Session, show_id: int, sent_date: date) -> Optional[Show]:
    """Mark an invoice as sent."""
    return update_show(session, show_id, invoice_sent=True, invoice_sent_date=sent_date)


def delete_show(session: Session, show_id: int) -> bool:
    """Delete a show."""
    show = get_show(session, show_id)
    if show:
        session.delete(show)
        session.flush()
        return True
    return False


# ============================================================================
# RecurringGig CRUD
# ============================================================================


def create_recurring_gig(session: Session, **kwargs) -> RecurringGig:
    """Create a new recurring gig."""
    gig = RecurringGig(**kwargs)
    session.add(gig)
    session.flush()
    return gig


def get_recurring_gig(session: Session, gig_id: int) -> Optional[RecurringGig]:
    """Get a recurring gig by ID."""
    return session.get(RecurringGig, gig_id)


def get_active_recurring_gigs(session: Session) -> list[RecurringGig]:
    """Get all active recurring gigs."""
    stmt = (
        select(RecurringGig)
        .options(joinedload(RecurringGig.venue))
        .where(RecurringGig.is_active == True)
    )
    return list(session.scalars(stmt).unique())


def get_recurring_gigs_for_venue(session: Session, venue_id: int) -> list[RecurringGig]:
    """Get all recurring gigs for a venue."""
    stmt = select(RecurringGig).where(RecurringGig.venue_id == venue_id)
    return list(session.scalars(stmt))


def update_recurring_gig(session: Session, gig_id: int, **kwargs) -> Optional[RecurringGig]:
    """Update a recurring gig."""
    gig = get_recurring_gig(session, gig_id)
    if gig:
        for key, value in kwargs.items():
            if hasattr(gig, key):
                setattr(gig, key, value)
        session.flush()
    return gig


def deactivate_recurring_gig(session: Session, gig_id: int) -> Optional[RecurringGig]:
    """Deactivate a recurring gig."""
    return update_recurring_gig(session, gig_id, is_active=False)


def delete_recurring_gig(session: Session, gig_id: int, cancel_future: bool = True) -> bool:
    """
    Delete a recurring gig.

    If cancel_future is True, also cancel all future show instances.
    """
    gig = get_recurring_gig(session, gig_id)
    if not gig:
        return False

    if cancel_future:
        today = date.today()
        for show in gig.shows:
            if show.date >= today:
                show.is_cancelled = True

    session.delete(gig)
    session.flush()
    return True


# ============================================================================
# ContactLog CRUD
# ============================================================================


def create_contact_log(session: Session, **kwargs) -> ContactLog:
    """Create a new contact log entry."""
    log = ContactLog(**kwargs)
    session.add(log)
    session.flush()
    return log


def get_contact_log(session: Session, log_id: int) -> Optional[ContactLog]:
    """Get a contact log by ID."""
    return session.get(ContactLog, log_id)


def get_contact_logs_for_venue(session: Session, venue_id: int) -> list[ContactLog]:
    """Get all contact logs for a venue, most recent first."""
    stmt = (
        select(ContactLog)
        .where(ContactLog.venue_id == venue_id)
        .order_by(ContactLog.contacted_at.desc())
    )
    return list(session.scalars(stmt))


def get_last_contact_for_venue(session: Session, venue_id: int) -> Optional[ContactLog]:
    """Get the most recent contact for a venue."""
    logs = get_contact_logs_for_venue(session, venue_id)
    return logs[0] if logs else None


def get_pending_follow_ups(session: Session) -> list[ContactLog]:
    """Get contact logs with follow-up dates in the past or today."""
    today = date.today()
    stmt = (
        select(ContactLog)
        .options(joinedload(ContactLog.venue))
        .where(ContactLog.follow_up_date <= today)
        .order_by(ContactLog.follow_up_date)
    )
    return list(session.scalars(stmt).unique())


def update_contact_log(session: Session, log_id: int, **kwargs) -> Optional[ContactLog]:
    """Update a contact log."""
    log = get_contact_log(session, log_id)
    if log:
        for key, value in kwargs.items():
            if hasattr(log, key):
                setattr(log, key, value)
        session.flush()
    return log


def delete_contact_log(session: Session, log_id: int) -> bool:
    """Delete a contact log."""
    log = get_contact_log(session, log_id)
    if log:
        session.delete(log)
        session.flush()
        return True
    return False
