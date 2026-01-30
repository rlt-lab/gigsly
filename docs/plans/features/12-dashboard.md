# Dashboard

## Overview

The Dashboard is the home screen - a quick glance at what needs attention and what's coming up.

## Screen Layout

```
┌─ Dashboard ──────────────────────────────────────────────────┐
│                                                              │
│  ╔═══════════════╗  ╔═══════════════╗  ╔═══════════════╗    │
│  ║  UPCOMING     ║  ║  YTD EARNED   ║  ║  UNPAID       ║    │
│  ║     7         ║  ║   $4,250      ║  ║   $350        ║    │
│  ║   shows       ║  ║               ║  ║  (2 shows)    ║    │
│  ╚═══════════════╝  ╚═══════════════╝  ╚═══════════════╝    │
│                                                              │
│  ─── NEXT 14 DAYS ──────────────────────────────────────────│
│                                                              │
│  Sat Feb 1   The Blue Note         $200   pending           │
│  Sat Feb 8   Ryman Auditorium      $350   pending           │
│  Fri Feb 14  3rd & Lindsley        $175   pending           │
│                                                              │
│  ─── NEEDS ATTENTION ───────────────────────────────────────│
│                                                              │
│  ⚠ 2 payments overdue                          [View →]     │
│  ⚠ 1 invoice needs sending                     [View →]     │
│  📅 Booking window opens in 3 days (Blue Note) [View →]     │
│                                                              │
│  [v] Venues  [s] Shows  [c] Calendar  [r] Full Report       │
└──────────────────────────────────────────────────────────────┘
```

## Stats Cards

### Upcoming Shows
- Count of shows where `date >= today`
- Tap/Enter to go to Shows screen (upcoming filter)

### YTD Earned
- Sum of `pay_amount` where `payment_status = 'paid'` and `date` is in current year
- Calculation: `SELECT SUM(pay_amount) FROM shows WHERE payment_status = 'paid' AND strftime('%Y', date) = strftime('%Y', 'now')`

### Unpaid Balance
- Sum of `pay_amount` where `payment_status = 'pending'` and `date < today`
- Shows count in parentheses
- Red highlight if amount > 0
- Tap/Enter to go to Shows screen (unpaid filter)

## Next 14 Days Section

- List of shows in the next 14 days
- Sorted by date ascending
- Shows: Day, Date, Venue Name, Pay, Status
- Maximum 5 shows displayed; if more, shows "... and X more"
- Empty state: "No shows in the next 2 weeks"

## Needs Attention Section

Priority-ordered list of action items (max 5 shown):

| Condition | Display | Priority |
|-----------|---------|----------|
| Shows unpaid > 30 days | "X payments overdue" | 1 |
| Shows needing invoice | "X invoices need sending" | 2 |
| Booking window ≤ 7 days | "Booking window opens in X days (Venue)" | 3 |
| No upcoming shows at venue | "No upcoming shows at Venue" | 4 |
| Contact > 60 days | "Haven't contacted Venue in X days" | 5 |

Each item has a `[View →]` action that navigates to the relevant screen/item.

If no items need attention: "✓ All caught up!"

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `v` | Go to Venues |
| `s` | Go to Shows |
| `c` | Go to Calendar |
| `r` | Go to Full Report |
| `Enter` | Activate selected item |
| `↑`/`↓` | Navigate items |
| `?` | Help |
| `q` | Quit application |

## Refresh Behavior

- Stats refresh on screen focus
- Background refresh every 60 seconds while visible
- Manual refresh with `Ctrl+R`

## Related Features

- [Shows](./03-shows.md)
- [Smart Reports](./08-smart-reports.md)
- [Calendar](./04-calendar.md)
