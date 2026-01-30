# Core Algorithms & Business Rules

## Overview

This document defines the exact algorithms and calculation rules used throughout Gigsly. All implementations must follow these specifications.

---

## Date & Time Handling

### Timezone Policy

All dates and times use **local device timezone**. No timezone conversion is performed.

```python
# All comparisons use local time
from datetime import date, datetime

def today():
    return date.today()  # Local date

def now():
    return datetime.now()  # Local datetime
```

### Days Calculation

Use **calendar days**, not exact 24-hour periods:

```python
def days_between(from_date: date, to_date: date) -> int:
    """Returns whole calendar days between dates."""
    return (to_date - from_date).days
```

**Examples**:
- Jan 30 11pm → Jan 31 1am = **1 day** (not 2 hours)
- Jan 1 → Jan 31 = **30 days**

---

## Contact Tracking

### Days Since Contact

```python
def days_since_contact(venue) -> int | None:
    """
    Returns days since most recent contact, or None if never contacted.
    Only counts contacts where contacted_at is set.
    """
    if not venue.contact_logs:
        return None  # Never contacted

    latest = max(log.contacted_at.date() for log in venue.contact_logs)
    return days_between(latest, today())
```

### Last Contact Date

For display purposes:

```python
def last_contact_date(venue) -> date | None:
    """Returns most recent contact date, regardless of outcome."""
    if not venue.contact_logs:
        return None
    return max(log.contacted_at.date() for log in venue.contact_logs)
```

### Contact Reminder Suppression

```python
def should_suppress_contact_reminder(venue) -> bool:
    """
    Suppress if:
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
```

---

## Booking Window

### Days Until Window Opens

```python
def days_until_booking_window(venue) -> int | None:
    """
    Returns days until booking window opens, or None if:
    - No window configured
    - Window is currently open
    """
    if not venue.booking_window_start:
        return None

    current_day = today().day
    start_day = venue.booking_window_start
    end_day = venue.booking_window_end or start_day

    # Check if window is currently open
    if is_booking_window_open(venue):
        return None  # Open now, not "days until"

    # Calculate days until start
    if current_day < start_day:
        # Window is later this month
        return start_day - current_day
    else:
        # Window is next month
        days_left_in_month = days_in_current_month() - current_day
        return days_left_in_month + start_day

def is_booking_window_open(venue) -> bool:
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
```

---

## Payment Status

### Overdue Calculation

```python
def payment_status_display(show) -> tuple[str, str]:
    """
    Returns (status_text, color) for display.
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

def needs_invoice(show, venue) -> bool:
    """
    Returns True if show needs invoice to be sent.
    """
    return (
        venue.requires_invoice and
        not show.invoice_sent and
        show.date < today() and  # Show has occurred
        show.payment_status == "pending"
    )
```

### Unpaid Balance

```python
def unpaid_balance() -> float:
    """
    Sum of pay_amount for all past unpaid shows.
    """
    return sum(
        show.pay_amount
        for show in all_shows()
        if show.date < today() and show.payment_status == "pending"
    )
```

---

## Recurring Instance Generation

### Trigger Events

Instance generation occurs on:
1. **App launch** - Generate missing instances for next 3 months
2. **Recurring gig creation** - Initial generation
3. **Manual refresh** - `Ctrl+R` on Calendar or Shows screen

### Generation Algorithm

```python
def generate_recurring_instances(recurring_gig):
    """
    Idempotent: Only creates instances for dates without existing shows.
    """
    window_end = today() + timedelta(days=90)  # 3 months

    for occurrence_date in iter_occurrences(recurring_gig, today(), window_end):
        # Skip if instance already exists
        existing = get_show_for_recurring_date(recurring_gig.id, occurrence_date)
        if existing:
            continue

        # Create new instance
        create_show(
            venue_id=recurring_gig.venue_id,
            recurring_gig_id=recurring_gig.id,
            date=occurrence_date,
            pay_amount=recurring_gig.pay_amount,
            payment_status="pending"
        )

def iter_occurrences(gig, start: date, end: date):
    """
    Yields all occurrence dates for a recurring pattern.
    Handles edge cases: fifth weekday, month-end dates.
    """
    if gig.pattern_type == "weekly":
        yield from iter_weekly(gig.start_date, gig.day_of_week, start, end)
    elif gig.pattern_type == "biweekly":
        yield from iter_weekly(gig.start_date, gig.day_of_week, start, end, interval=2)
    elif gig.pattern_type == "monthly_date":
        yield from iter_monthly_date(gig.day_of_month, start, end)
    elif gig.pattern_type == "monthly_ordinal":
        yield from iter_monthly_ordinal(gig.ordinal, gig.day_of_week, start, end)
    elif gig.pattern_type == "custom":
        yield from iter_weekly(gig.start_date, gig.day_of_week, start, end, gig.interval_weeks)
```

### Pattern Field Usage

| Pattern Type | day_of_week | day_of_month | ordinal | interval_weeks |
|--------------|-------------|--------------|---------|----------------|
| weekly | 0-6 | - | - | - |
| biweekly | 0-6 | - | - | (implicit: 2) |
| monthly_date | - | 1-31 | - | - |
| monthly_ordinal | 0-6 | - | 1-5 | - |
| custom | 0-6 | - | - | N |

### Edge Case Handling

**Fifth weekday problem**:
```python
def iter_monthly_ordinal(ordinal, day_of_week, start, end):
    """Skip months where ordinal doesn't exist (e.g., 5th Friday)."""
    for month in iter_months(start, end):
        date = nth_weekday_of_month(ordinal, day_of_week, month)
        if date:  # None if doesn't exist
            yield date
```

**Month-end dates** (e.g., 31st):
```python
def iter_monthly_date(day_of_month, start, end):
    """Use last day of month if day doesn't exist."""
    for month in iter_months(start, end):
        last_day = days_in_month(month)
        actual_day = min(day_of_month, last_day)
        yield date(month.year, month.month, actual_day)
```

---

## Smart Report Scoring

### Priority Score Algorithm

```python
def calculate_venue_score(venue) -> int:
    """
    Calculate priority score for a venue.
    Higher score = needs more attention.
    Score is uncapped (can exceed 100).
    """
    score = 0

    # === GET PAID (payment issues) ===
    overdue_shows = [s for s in venue.shows
                     if s.payment_status == "pending"
                     and days_between(s.date, today()) >= 30]
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

    upcoming_count = len([s for s in venue.shows if s.date >= today()])
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
```

### Section Assignment

```python
def assign_report_section(venue, score) -> str | None:
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
```

### Color Coding

| Score Range | Color |
|-------------|-------|
| 50+ | Red (urgent) |
| 25-49 | Yellow (attention) |
| 1-24 | Green (low priority) |

---

## Search & Filter

### Search Scope

The `/` search command searches:
- **Venues**: name, location, contact_name (case-insensitive substring)
- **Shows**: venue name, notes (case-insensitive substring)

```python
def search_venues(query: str):
    q = query.lower()
    return [v for v in all_venues()
            if q in (v.name or "").lower()
            or q in (v.location or "").lower()
            or q in (v.contact_name or "").lower()]
```

### Filter Behavior

Filters are **mutually exclusive** (radio buttons, not checkboxes):
- Selecting a filter replaces the previous filter
- "All" shows everything (default)

---

## Data Invariants

### Validation Rules

These invariants must be enforced at the database/model layer:

```python
# Show invariants
assert show.invoice_sent == False or show.invoice_sent_date is not None
assert show.payment_status == "paid" or show.payment_received_date is None
assert show.payment_received_date is None or show.payment_received_date >= show.date

# Recurring gig invariants
assert recurring_gig.end_date is None or recurring_gig.end_date >= recurring_gig.start_date

# Booking window invariants
assert venue.booking_window_start is None or 1 <= venue.booking_window_start <= 31
assert venue.booking_window_end is None or 1 <= venue.booking_window_end <= 31
```

### Venue Deletion

When a venue is deleted:
1. **Past shows**: Preserve with denormalized `venue_name_snapshot` field
2. **Future shows**: Cancel (set `is_cancelled = True`)
3. **Recurring gigs**: Deactivate (set `is_active = False`)
4. **Contact logs**: Preserve for history (orphaned is OK)

```python
def delete_venue(venue):
    # Snapshot venue name on past shows
    for show in venue.shows:
        if show.date < today():
            show.venue_name_snapshot = venue.name
            show.venue_id = None  # Orphan the show
        else:
            show.is_cancelled = True

    # Deactivate recurring gigs
    for gig in venue.recurring_gigs:
        gig.is_active = False

    # Actually delete the venue
    delete(venue)
```

---

## Related Features

- [Data Model](./01-data-model.md)
- [Smart Reports](./08-smart-reports.md)
- [Recurring Gigs](./05-recurring-gigs.md)
- [Contact Tracking](./07-contact-tracking.md)
