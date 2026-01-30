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
│ Outcome: [Awaiting Response ▼]                           │
│          • Booked                                         │
│          • Declined                                       │
│          • Awaiting Response                              │
│          • Follow Up Needed                               │
│          • Other                                          │
│                                                           │
│ Follow up on: [________] (optional)                      │
│                                                           │
│ Notes:  [________________________________]               │
│         [________________________________]               │
│                                                           │
│                        [Save]  [Cancel]                   │
└───────────────────────────────────────────────────────────┘
```

### Outcome Values

| Outcome | Meaning | Effect on Smart Report |
|---------|---------|------------------------|
| Booked | Gig was booked from this contact | Venue deprioritized for booking outreach |
| Declined | Venue said no | Resets contact reminder (try again later) |
| Awaiting Response | Waiting to hear back | Suppresses "needs contact" for 14 days |
| Follow Up Needed | Need to reach out again | Adds to "Stay in Touch" with higher priority |
| Other | General contact | Normal contact reminder reset |

### Outcome Effect Clarifications

**Awaiting Response (14-day suppression)**:
- Timer starts from `contacted_at` date, not entry date
- After 14 days, contact reminder automatically reappears
- If user contacts again before 14 days, new contact resets the timer
- Multiple "Awaiting Response" entries: most recent one is used

**Follow Up Date**:
- If `follow_up_date` is set and in the future, contact reminders are also suppressed
- Follow-up takes precedence over 14-day awaiting response window
- When follow-up date arrives, venue appears in Dashboard "Needs Attention"

See: [Algorithms](./13-algorithms.md) for exact calculation rules

## Contact History View

In venue detail, option to view full contact history:

```
┌─ Contact History: The Blue Note ──────────────────────────┐
│                                                           │
│ 2025-01-30  Email   Awaiting    Asked about March dates  │
│ 2025-01-15  Phone   Booked      Confirmed Feb 1 show     │
│ 2024-12-10  Email   Awaiting    Initial booking inquiry  │
│ 2024-11-05  In Person  Booked   Met at open mic          │
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

## Follow-Up Reminders

When a contact has `follow_up_date` set:
- Appears in Dashboard "Needs Attention" section on that date
- Included in Smart Report with elevated priority
- Shows notification badge on Venues screen

## Related Features

- [Venues](./02-venues.md)
- [Smart Reports](./08-smart-reports.md)
- [Algorithms](./13-algorithms.md)
