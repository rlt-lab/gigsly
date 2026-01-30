"""Core algorithms and business rules for Gigsly.

Implements the exact algorithms defined in docs/plans/features/13-algorithms.md.
"""

import calendar
from datetime import date, timedelta
from typing import Iterator, Literal, Optional

from gigsly.db.models import RecurringGig, Show, Venue


# ============================================================================
# Date & Time Helpers
# ============================================================================


def today() -> date:
    """Returns the current local date."""
    return date.today()


def days_between(from_date: date, to_date: date) -> int:
    """Returns whole calendar days between dates."""
    return (to_date - from_date).days


def days_in_month(year: int, month: int) -> int:
    """Returns the number of days in a given month."""
    return calendar.monthrange(year, month)[1]


def days_in_current_month() -> int:
    """Returns the number of days in the current month."""
    t = today()
    return days_in_month(t.year, t.month)


# ============================================================================
# Contact Tracking
# ============================================================================


def days_since_contact(venue: Venue) -> Optional[int]:
    """
    Returns days since most recent contact, or None if never contacted.
    Only counts contacts where contacted_at is set.
    """
    if not venue.contact_logs:
        return None

    latest = max(log.contacted_at.date() for log in venue.contact_logs)
    return days_between(latest, today())


def last_contact_date(venue: Venue) -> Optional[date]:
    """Returns most recent contact date, regardless of outcome."""
    if not venue.contact_logs:
        return None
    return max(log.contacted_at.date() for log in venue.contact_logs)


def should_suppress_contact_reminder(venue: Venue) -> bool:
    """
    Suppress contact reminder if:
    - "Awaiting Response" within last 14 days
    - Has follow_up_date in the future
    """
    for log in venue.contact_logs:
        # Awaiting response within 14 days
        if log.outcome == "awaiting_response":
            if days_between(log.contacted_at.date(), today()) < 14:
                return True

        # Future follow-up scheduled
        if log.follow_up_date and log.follow_up_date > today():
            return True

    return False


# ============================================================================
# Booking Window
# ============================================================================


def is_booking_window_open(venue: Venue) -> bool:
    """Returns True if booking window is currently open."""
    if not venue.booking_window_start:
        return False

    current_day = today().day
    start_day = venue.booking_window_start
    end_day = venue.booking_window_end or start_day

    if start_day <= end_day:
        # Normal range: start <= current <= end
        return start_day <= current_day <= end_day
    else:
        # Wraps around month (e.g., 25th to 5th)
        return current_day >= start_day or current_day <= end_day


def days_until_booking_window(venue: Venue) -> Optional[int]:
    """
    Returns days until booking window opens, or None if:
    - No window configured
    - Window is currently open
    """
    if not venue.booking_window_start:
        return None

    # Check if window is currently open
    if is_booking_window_open(venue):
        return None  # Open now, not "days until"

    current_day = today().day
    start_day = venue.booking_window_start

    # Calculate days until start
    if current_day < start_day:
        # Window is later this month
        return start_day - current_day
    else:
        # Window is next month
        days_left_in_month = days_in_current_month() - current_day
        return days_left_in_month + start_day


# ============================================================================
# Payment Status
# ============================================================================


def payment_status_display(show: Show) -> tuple[str, str]:
    """
    Returns (status_text, color) for display.
    Color values: "green", "gray", "yellow", "red"
    """
    if show.payment_status == "paid":
        return ("paid", "green")

    # Show is pending
    if show.date >= today():
        return ("pending", "gray")

    days_unpaid = days_between(show.date, today())

    if days_unpaid >= 30:
        return (f"OVERDUE ({days_unpaid}d)", "red")
    else:
        return (f"UNPAID ({days_unpaid}d)", "yellow")


def needs_invoice(show: Show, venue: Optional[Venue] = None) -> bool:
    """
    Returns True if show needs invoice to be sent.
    """
    v = venue or show.venue
    if not v:
        return False

    return (
        v.requires_invoice
        and not show.invoice_sent
        and show.date < today()  # Show has occurred
        and show.payment_status == "pending"
    )


def unpaid_balance(shows: list[Show]) -> float:
    """
    Sum of pay_amount for all past unpaid shows.
    """
    return sum(
        show.pay_amount or 0
        for show in shows
        if show.date < today() and show.payment_status == "pending"
    )


# ============================================================================
# Recurring Instance Generation
# ============================================================================


def iter_months(start: date, end: date) -> Iterator[date]:
    """Yields the first day of each month in the range."""
    current = date(start.year, start.month, 1)
    while current <= end:
        yield current
        # Move to next month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)


def nth_weekday_of_month(ordinal: int, weekday: int, month_start: date) -> Optional[date]:
    """
    Returns the nth occurrence of weekday in the given month.
    Returns None if it doesn't exist (e.g., 5th Friday in a month with only 4).

    ordinal: 1-5 (1st, 2nd, 3rd, 4th, 5th)
    weekday: 0-6 (Monday-Sunday)
    """
    year, month = month_start.year, month_start.month

    # Find first occurrence of weekday in this month
    first_day = date(year, month, 1)
    days_until_weekday = (weekday - first_day.weekday()) % 7
    first_occurrence = first_day + timedelta(days=days_until_weekday)

    # Calculate nth occurrence
    target = first_occurrence + timedelta(weeks=ordinal - 1)

    # Check if still in same month
    if target.month != month:
        return None

    return target


def iter_weekly(
    pattern_start: date, day_of_week: int, start: date, end: date, interval: int = 1
) -> Iterator[date]:
    """
    Yields weekly/biweekly/custom interval occurrences.

    pattern_start: When the pattern began (anchor date)
    day_of_week: 0-6 (Monday-Sunday)
    start, end: Range to generate
    interval: Weeks between occurrences (1=weekly, 2=biweekly)
    """
    # Find first occurrence of day_of_week on or after pattern_start
    days_until_weekday = (day_of_week - pattern_start.weekday()) % 7
    first_occurrence = pattern_start + timedelta(days=days_until_weekday)

    # Calculate which interval we should start from
    if start > first_occurrence:
        weeks_elapsed = (start - first_occurrence).days // 7
        intervals_elapsed = weeks_elapsed // interval
        current = first_occurrence + timedelta(weeks=intervals_elapsed * interval)
        # Make sure we're at or after start
        while current < start:
            current += timedelta(weeks=interval)
    else:
        current = first_occurrence

    # Yield occurrences in range
    while current <= end:
        if current >= start:
            yield current
        current += timedelta(weeks=interval)


def iter_monthly_date(day_of_month: int, start: date, end: date) -> Iterator[date]:
    """
    Yields monthly occurrences on a specific day of month.
    Uses last day of month if day doesn't exist.
    """
    for month_start in iter_months(start, end):
        last_day = days_in_month(month_start.year, month_start.month)
        actual_day = min(day_of_month, last_day)
        occurrence = date(month_start.year, month_start.month, actual_day)
        if start <= occurrence <= end:
            yield occurrence


def iter_monthly_ordinal(
    ordinal: int, day_of_week: int, start: date, end: date
) -> Iterator[date]:
    """
    Yields monthly occurrences like "2nd Tuesday" or "4th Friday".
    Skips months where ordinal doesn't exist (e.g., 5th Friday).
    """
    for month_start in iter_months(start, end):
        occurrence = nth_weekday_of_month(ordinal, day_of_week, month_start)
        if occurrence and start <= occurrence <= end:
            yield occurrence


def iter_occurrences(gig: RecurringGig, start: date, end: date) -> Iterator[date]:
    """
    Yields all occurrence dates for a recurring pattern.
    Handles edge cases: fifth weekday, month-end dates.
    """
    # Respect gig's own date boundaries
    effective_start = max(start, gig.start_date)
    effective_end = end
    if gig.end_date:
        effective_end = min(end, gig.end_date)

    if effective_start > effective_end:
        return

    if gig.pattern_type == "weekly":
        yield from iter_weekly(gig.start_date, gig.day_of_week, effective_start, effective_end)
    elif gig.pattern_type == "biweekly":
        yield from iter_weekly(
            gig.start_date, gig.day_of_week, effective_start, effective_end, interval=2
        )
    elif gig.pattern_type == "monthly_date":
        yield from iter_monthly_date(gig.day_of_month, effective_start, effective_end)
    elif gig.pattern_type == "monthly_ordinal":
        yield from iter_monthly_ordinal(
            gig.ordinal, gig.day_of_week, effective_start, effective_end
        )
    elif gig.pattern_type == "custom":
        yield from iter_weekly(
            gig.start_date, gig.day_of_week, effective_start, effective_end, gig.interval_weeks
        )


# ============================================================================
# Smart Report Scoring
# ============================================================================


def has_payment_issues(venue: Venue) -> bool:
    """Returns True if venue has any payment-related issues."""
    for show in venue.shows:
        if show.payment_status == "pending" and show.date < today():
            days_unpaid = days_between(show.date, today())
            if days_unpaid >= 30:
                return True
            if needs_invoice(show, venue):
                return True
    return False


def has_booking_opportunity(venue: Venue) -> bool:
    """Returns True if venue has a booking opportunity."""
    if is_booking_window_open(venue):
        return True

    days_until = days_until_booking_window(venue)
    if days_until is not None and days_until <= 7:
        return True

    # Low upcoming shows
    upcoming_count = sum(1 for s in venue.shows if s.date >= today() and not s.is_cancelled)
    if upcoming_count <= 2:
        return True

    return False


def needs_contact(venue: Venue) -> bool:
    """Returns True if venue needs to be contacted."""
    if should_suppress_contact_reminder(venue):
        return False

    days_since = days_since_contact(venue)
    return days_since is None or days_since >= 60


def calculate_venue_score(venue: Venue) -> int:
    """
    Calculate priority score for a venue.
    Higher score = needs more attention.
    Score is uncapped (can exceed 100).
    """
    score = 0
    t = today()

    # === GET PAID (payment issues) ===
    overdue_shows = [
        s
        for s in venue.shows
        if s.payment_status == "pending" and days_between(s.date, t) >= 30
    ]
    if overdue_shows:
        score += 35  # First overdue
        score += 15 * (len(overdue_shows) - 1)  # Each additional

    pending_invoices = [s for s in venue.shows if needs_invoice(s, venue)]
    if pending_invoices:
        score += 30  # First pending invoice
        score += 10 * (len(pending_invoices) - 1)  # Each additional

    # === BOOK SHOWS (booking opportunities) ===
    if is_booking_window_open(venue):
        score += 25
    elif (days := days_until_booking_window(venue)) is not None:
        if days <= 3:
            score += 20
        elif days <= 7:
            score += 10

    upcoming_count = sum(1 for s in venue.shows if s.date >= t and not s.is_cancelled)
    if upcoming_count == 0:
        score += 10
    elif upcoming_count <= 2:
        score += 5

    # === STAY IN TOUCH (contact reminders) ===
    if not should_suppress_contact_reminder(venue):
        days_since = days_since_contact(venue)
        if days_since is None or days_since >= 90:
            score += 5
        elif days_since >= 60:
            score += 3

    return score


ReportSection = Literal["GET_PAID", "BOOK_SHOWS", "STAY_IN_TOUCH"]


def assign_report_section(venue: Venue, score: int) -> Optional[ReportSection]:
    """
    Assigns venue to a report section based on primary condition.
    Returns None if venue shouldn't appear in report.
    """
    if score == 0:
        return None

    # Check conditions in priority order
    if has_payment_issues(venue):
        return "GET_PAID"
    elif has_booking_opportunity(venue):
        return "BOOK_SHOWS"
    elif needs_contact(venue):
        return "STAY_IN_TOUCH"

    return None  # Score from multiple small factors, no primary section


def score_color(score: int) -> str:
    """Returns color based on score range."""
    if score >= 50:
        return "red"
    elif score >= 25:
        return "yellow"
    else:
        return "green"
