# Contact Tracking

## Overview

Track when you reach out to venues for booking. Combined with booking windows and show counts, this powers the smart report's contact recommendations.

## Contact Log Entry

From venue detail view, press `c` to log contact:

```
┌─ Log Contact ─────────────────────────────────────────────┐
│                                                           │
│ Venue: The Blue Note                                      │
│                                                           │
│ Date:   [2025-01-30    ] (defaults to today)             │
│                                                           │
│ Method: [Email         ▼]                                │
│         • Email                                           │
│         • Phone                                           │
│         • In Person                                       │
│         • Other                                           │
│                                                           │
│ Notes:  [________________________________]               │
│         [________________________________]               │
│         [________________________________]               │
│                                                           │
│                        [Save]  [Cancel]                   │
└───────────────────────────────────────────────────────────┘
```

## Contact History View

In venue detail, option to view full contact history:

```
┌─ Contact History: The Blue Note ──────────────────────────┐
│                                                           │
│ 2025-01-30  Email   Asked about March dates              │
│ 2025-01-15  Phone   Confirmed Feb 1 show                 │
│ 2024-12-10  Email   Initial booking inquiry              │
│ 2024-11-05  In Person  Met at open mic                   │
│                                                           │
│ [n] New Contact  [q] Close                               │
└───────────────────────────────────────────────────────────┘
```

## Booking Windows

Venues can have a booking window - the days of the month when they're actively booking.

**Example**: A venue books on the 1st-7th of each month.

### Alert Logic

Given `booking_window_start = 1` and `booking_window_end = 7`:

| Today's Date | Days Until Window | Alert Level |
|--------------|-------------------|-------------|
| Jan 20 | 11 days | None |
| Jan 25 | 6 days | "Window opens in 6 days" (yellow) |
| Jan 29 | 2 days | "Window opens in 2 days" (orange) |
| Feb 1 | Now open | "Booking window OPEN" (red) |
| Feb 5 | Open, 2 days left | "Window closes in 2 days" (red) |

## Venue Display

In venue list, "Last Contact" column shows:
- Date of most recent contact log entry
- If no entries: "Never"
- Color coding: red if > 90 days, yellow if > 60 days

## Related Features

- [Venues](./02-venues.md)
- [Smart Reports](./08-smart-reports.md)
