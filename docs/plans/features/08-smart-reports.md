# Smart Reports

## Overview

The smart report is the primary tool for knowing what needs your attention. It uses priority scoring to surface the most urgent items first.

## Access

- **TUI**: Dashboard → Report screen, or press `r` from anywhere
- **CLI**: `gigsly report` (prints to terminal, no TUI needed)

## Priority Scoring Algorithm

Each venue is scored 0-100 based on these factors:

| Factor | Weight | Scoring |
|--------|--------|---------|
| Unpaid gigs | 35 pts | +35 per unpaid gig > 30 days old |
| Invoice pending | 30 pts | +30 per completed gig needing invoice |
| Booking window approaching | 20 pts | +20 if ≤7 days, +10 if ≤14 days |
| Low show count | 10 pts | +10 if 0 upcoming, +5 if 1-2 upcoming |
| Days since contact | 5 pts | +5 if 90+ days, +3 if 60-89 days |

**Priority levels:**
- **Critical** (50+): Red, needs immediate action
- **Attention** (25-49): Yellow, handle soon
- **Monitor** (1-24): Low priority, informational

## Report Layout

```
═══════════════════════════════════════════════════════════
                    GIGSLY ACTION REPORT
                      January 30, 2025
═══════════════════════════════════════════════════════════

─── GET PAID ──────────────────────────────────────────────

⚠ OVERDUE: Exit/In - $150 (35 days unpaid)
  → Last show: Dec 26, 2024

⚠ INVOICE NEEDED: Acme Corp - $500
  → Show completed: Jan 20, 2025
  → Venue requires invoice

─── BOOK SHOWS ────────────────────────────────────────────

🔴 CRITICAL: The Blue Note [Score: 55]
  → Booking window opens in 2 days (Feb 1-7)
  → Only 1 upcoming show
  → Last contact: 45 days ago

🟡 ATTENTION: Ryman Auditorium [Score: 30]
  → 0 upcoming shows after Feb 8
  → Last contact: 62 days ago

─── STAY IN TOUCH ─────────────────────────────────────────

🟢 MONITOR: 3rd & Lindsley [Score: 8]
  → Last contact: 75 days ago
  → 2 upcoming shows (stable)

═══════════════════════════════════════════════════════════
Summary: 2 payment issues, 2 booking priorities, 1 contact
═══════════════════════════════════════════════════════════
```

## CLI Output

`gigsly report` produces the same output, formatted for terminal:

```bash
$ gigsly report

GIGSLY ACTION REPORT - January 30, 2025

GET PAID
  ! OVERDUE: Exit/In - $150 (35 days)
  ! INVOICE: Acme Corp - $500

BOOK SHOWS
  [55] The Blue Note - window opens in 2 days, 1 upcoming show
  [30] Ryman Auditorium - 0 upcoming shows, 62 days since contact

STAY IN TOUCH
  [ 8] 3rd & Lindsley - 75 days since contact

Summary: 2 payment, 2 booking, 1 contact
```

## Configurable Thresholds

In `~/.gigsly/config.toml`:

```toml
[thresholds]
payment_overdue_days = 30
low_show_count = 2
contact_reminder_days = 60
booking_window_alert_days = 7
```

## Related Features

- [Payments](./06-payments.md)
- [Contact Tracking](./07-contact-tracking.md)
- [Tax Reports](./09-tax-reports.md)
