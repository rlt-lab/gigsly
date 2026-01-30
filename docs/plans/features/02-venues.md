# Venues

## Overview

Venues are the core entity - locations where you perform. Each venue stores contact information, payment preferences, booking windows, and mileage.

## Screen Layout

### Venue List View

```
┌─ Venues ──────────────────────────────────────────────────┐
│ [Search: ___________]  [Filter: All ▼]                    │
│                                                           │
│ Name              Location      Last Contact  Upcoming    │
│ ─────────────────────────────────────────────────────────│
│ The Blue Note     Nashville     2025-01-15    3 shows    │
│ Ryman Auditorium  Nashville     2024-12-01    1 show     │
│ Exit/In           Nashville     2024-11-20    0 shows    │
│ 3rd & Lindsley    Nashville     2025-01-28    2 shows    │
│                                                           │
│ [n] New  [Enter] View  [/] Search  [q] Back              │
└───────────────────────────────────────────────────────────┘
```

### Venue Detail View

```
┌─ The Blue Note ───────────────────────────────────────────┐
│                                                           │
│ Location:     Nashville, TN                               │
│ Address:      123 Music Row, Nashville, TN 37203          │
│ Contact:      Jane Smith                                  │
│ Email:        jane@bluenote.com                           │
│ Phone:        (615) 555-1234                              │
│                                                           │
│ ─── Booking ──────────────────────────────────────────── │
│ Mileage:      12 miles (24 mi round trip)                │
│ Typical Pay:  $200                                        │
│ Payment:      Check                                       │
│ Invoice Req:  Yes                                         │
│ W-9 on File:  Yes                                         │
│ Books:        1st - 7th of each month                     │
│                                                           │
│ ─── Stats ────────────────────────────────────────────── │
│ Total Shows:  15                                          │
│ Total Earned: $2,850                                      │
│ Upcoming:     3 shows                                     │
│ Last Contact: 2025-01-15 (15 days ago)                   │
│                                                           │
│ [e] Edit  [c] Log Contact  [s] Shows  [q] Back           │
└───────────────────────────────────────────────────────────┘
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `n` | Add new venue |
| `Enter` | View venue details |
| `e` | Edit venue (in detail view) |
| `d` | Delete venue (in detail view) |
| `c` | Log contact (in detail view) |
| `s` | View shows at this venue |
| `/` | Focus search |
| `q` | Go back |

## Delete Venue

Press `d` in venue detail view to delete:

```
┌─ Delete Venue ────────────────────────────────────────────────┐
│                                                               │
│  ⚠ Delete "The Blue Note"?                                   │
│                                                               │
│  This venue has:                                              │
│    • 15 past shows ($2,850 total)                            │
│    • 3 upcoming shows                                         │
│    • 1 active recurring gig                                   │
│                                                               │
│  Deleting will:                                               │
│    • Cancel all upcoming shows                                │
│    • End all recurring gigs                                   │
│    • Keep past shows for tax records (venue name preserved)   │
│                                                               │
│  Type "DELETE" to confirm: [________]                        │
│                                                               │
│                                    [Cancel]                   │
└───────────────────────────────────────────────────────────────┘
```

### Deletion Behavior

- **Past shows**: Retained with venue name denormalized (for tax records)
- **Upcoming shows**: Marked as cancelled
- **Recurring gigs**: Ended (end_date set to today)
- **Contact logs**: Retained for historical record
- Requires typing "DELETE" to prevent accidental deletion

## Add/Edit Venue Form

Fields in order:
1. Name (required)
2. Location (city/area)
3. Address
4. Contact name
5. Contact email
6. Contact phone
7. Mileage (one-way)
8. Typical pay
9. Payment method (dropdown)
10. Requires invoice (checkbox)
11. W-9 on file (checkbox)
12. Booking window start (day of month)
13. Booking window end (day of month)
14. Notes

## Filtering Options

- All venues
- Has upcoming shows
- No upcoming shows
- Needs contact (60+ days)
- Booking window soon

## Related Features

- [Data Model](./01-data-model.md)
- [Shows](./03-shows.md)
- [Contact Tracking](./07-contact-tracking.md)
