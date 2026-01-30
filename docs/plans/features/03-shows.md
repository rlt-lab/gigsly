# Shows

## Overview

Shows represent individual gigs. Each show is linked to a venue and tracks date, payment amount, and payment status.

## Screen Layout

### Show List View

```
┌─ Shows ───────────────────────────────────────────────────┐
│ [Filter: Upcoming ▼]                                      │
│                                                           │
│ Date        Venue              Pay      Status            │
│ ─────────────────────────────────────────────────────────│
│ 2025-02-01  The Blue Note      $200     pending          │
│ 2025-02-08  Ryman Auditorium   $350     pending          │
│ 2025-02-14  3rd & Lindsley     $175     pending          │
│ 2025-01-25  Exit/In            $150     UNPAID (5d)      │
│ 2025-01-18  The Blue Note      $200     paid             │
│                                                           │
│ [n] New  [N] New + Venue  [Enter] View  [p] Mark Paid    │
└───────────────────────────────────────────────────────────┘
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `n` | Quick add show (existing venue) |
| `N` | Add show with new venue |
| `Enter` | View/edit show details |
| `p` | Mark as paid |
| `i` | Mark invoice sent |
| `d` | Delete show |
| `q` | Go back |

## Add Show Flow

### Quick Add (`n`)

1. **Venue selection**: Searchable dropdown of existing venues
2. **Date**: Date picker, defaults to next available date
3. **Pay amount**: Pre-fills from venue's typical_pay
4. **Done**: Creates show, returns to list

### Add with New Venue (`N`)

1. **Venue name**: Text input (required)
2. **Venue location**: Text input (optional)
3. **Date**: Date picker
4. **Pay amount**: Text input
5. **Done**: Creates venue (minimal info) + show, flash message to edit venue later

## Show Detail View

```
┌─ Show: Feb 1, 2025 ───────────────────────────────────────┐
│                                                           │
│ Venue:      The Blue Note                                 │
│ Date:       Saturday, February 1, 2025                    │
│ Pay:        $200                                          │
│ Status:     Pending                                       │
│                                                           │
│ ─── Payment ──────────────────────────────────────────── │
│ Invoice Required: Yes                                     │
│ Invoice Sent:     No                                      │
│                                                           │
│ ─── Recurring ────────────────────────────────────────── │
│ Part of: Every Saturday at The Blue Note                  │
│                                                           │
│ Notes:                                                    │
│ (none)                                                    │
│                                                           │
│ [e] Edit  [p] Mark Paid  [i] Send Invoice  [q] Back      │
└───────────────────────────────────────────────────────────┘
```

## Filter Options

- Upcoming (default)
- Past
- All
- Unpaid (past shows, payment_status = pending)
- Needs invoice

## Status Display Logic

| Condition | Display |
|-----------|---------|
| Future show, pending | "pending" (neutral) |
| Past show, pending, < 30 days | "UNPAID (Xd)" (yellow) |
| Past show, pending, >= 30 days | "OVERDUE (Xd)" (red) |
| Paid | "paid" (green) |

## Related Features

- [Data Model](./01-data-model.md)
- [Venues](./02-venues.md)
- [Recurring Gigs](./05-recurring-gigs.md)
- [Payments](./06-payments.md)
