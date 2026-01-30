# Data Model

## Overview

Gigsly uses SQLite with SQLAlchemy ORM. All data stored in `~/.gigsly/gigsly.db`.

## Tables

### Venue

Primary record for locations where you perform.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Venue name (required) |
| location | TEXT | City/area |
| address | TEXT | Full street address |
| contact_name | TEXT | Booking contact person |
| contact_email | TEXT | Email address |
| contact_phone | TEXT | Phone number |
| mileage_one_way | REAL | Miles from home (one-way) |
| typical_pay | REAL | Default pay rate |
| payment_method | TEXT | cash, check, venmo, cashapp, paypal, direct_deposit |
| requires_invoice | BOOLEAN | Whether venue needs invoice |
| has_w9 | BOOLEAN | W-9 on file for tax purposes |
| booking_window_start | INTEGER | Day of month booking opens (1-31) |
| booking_window_end | INTEGER | Day of month booking closes (1-31) |
| notes | TEXT | Free-form notes |
| created_at | DATETIME | Record creation timestamp |
| updated_at | DATETIME | Last update timestamp |

### Show

Individual gig/performance record.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| venue_id | INTEGER | Foreign key to Venue |
| recurring_gig_id | INTEGER | Foreign key to RecurringGig (nullable) |
| date | DATE | Show date |
| start_time | TIME | Gig start time (nullable) |
| end_time | TIME | Gig end time (nullable) |
| pay_amount | REAL | Payment for this show |
| payment_status | TEXT | pending, paid |
| payment_received_date | DATE | When payment was received |
| invoice_sent | BOOLEAN | Whether invoice was sent (if required) |
| invoice_sent_date | DATE | When invoice was sent |
| is_cancelled | BOOLEAN | For skipped recurring instances |
| notes | TEXT | Free-form notes |
| created_at | DATETIME | Record creation timestamp |
| updated_at | DATETIME | Last update timestamp |

### RecurringGig

Pattern definition for repeating shows.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| venue_id | INTEGER | Foreign key to Venue |
| pay_amount | REAL | Default pay for instances |
| pattern_type | TEXT | weekly, biweekly, monthly_date, monthly_ordinal, custom |
| day_of_week | INTEGER | 0-6 (Mon-Sun) for weekly patterns |
| day_of_month | INTEGER | 1-31 for monthly_date |
| ordinal | INTEGER | 1-5 for "first", "second", etc. |
| interval_weeks | INTEGER | For custom intervals |
| start_date | DATE | When recurrence begins |
| end_date | DATE | When recurrence ends (nullable = ongoing) |
| is_active | BOOLEAN | Whether still generating instances |
| created_at | DATETIME | Record creation timestamp |
| updated_at | DATETIME | Last update timestamp |

### ContactLog

Track outreach to venues.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| venue_id | INTEGER | Foreign key to Venue |
| contacted_at | DATETIME | When contact was made |
| method | TEXT | email, phone, in_person, other |
| outcome | TEXT | booked, declined, awaiting_response, follow_up_needed, other (nullable) |
| follow_up_date | DATE | When to follow up (nullable) |
| notes | TEXT | What was discussed |
| created_at | DATETIME | Record creation timestamp |

## Relationships

```
Venue (1) ──── (*) Show
  │
  ├──── (*) RecurringGig ──── (*) Show
  │
  └──── (*) ContactLog
```

## Indexes

- `show_venue_id_idx` on Show(venue_id)
- `show_date_idx` on Show(date)
- `show_recurring_gig_id_idx` on Show(recurring_gig_id)
- `contact_log_venue_id_idx` on ContactLog(venue_id)
- `recurring_gig_venue_id_idx` on RecurringGig(venue_id)

## Invariants & Validation Rules

These constraints must be enforced at the database/model layer:

### Show Constraints

| Constraint | Rule |
|------------|------|
| Invoice date consistency | If `invoice_sent = false`, then `invoice_sent_date` must be `NULL` |
| Payment date consistency | If `payment_status = "pending"`, then `payment_received_date` must be `NULL` |
| Payment date validity | `payment_received_date` must be >= `date` (can't be paid before the show) |
| Venue reference | `venue_id` can be `NULL` only for orphaned past shows (venue deleted) |
| Orphaned shows | If `venue_id = NULL`, then `venue_name_snapshot` must be set |

### Venue Constraints

| Constraint | Rule |
|------------|------|
| Booking window range | `booking_window_start` and `booking_window_end` must be 1-31 or `NULL` |
| Mileage non-negative | `mileage_one_way` must be >= 0 or `NULL` |
| Payment method enum | `payment_method` must be one of: cash, check, venmo, cashapp, paypal, direct_deposit, or `NULL` |

### RecurringGig Constraints

| Constraint | Rule |
|------------|------|
| Date range | If `end_date` is set, it must be >= `start_date` |
| Pattern type enum | `pattern_type` must be: weekly, biweekly, monthly_date, monthly_ordinal, custom |
| Day of week range | `day_of_week` must be 0-6 (Monday-Sunday) when used |
| Day of month range | `day_of_month` must be 1-31 when used |
| Ordinal range | `ordinal` must be 1-5 when used |

### ContactLog Constraints

| Constraint | Rule |
|------------|------|
| Method enum | `method` must be: email, phone, in_person, other |
| Outcome enum | `outcome` must be: booked, declined, awaiting_response, follow_up_needed, other, or `NULL` |

## Additional Fields (Not in Base Schema)

For venue deletion support, Show needs an additional field:

| Column | Type | Description |
|--------|------|-------------|
| venue_name_snapshot | TEXT | Preserved venue name when venue is deleted |

## Related Features

- [Venues](./02-venues.md)
- [Shows](./03-shows.md)
- [Recurring Gigs](./05-recurring-gigs.md)
- [Algorithms](./13-algorithms.md)
