# Payments

## Overview

Track payment status for each gig, handle invoicing requirements, and surface overdue payments in reports.

## Payment Status Workflow

```
Show Created
     │
     ▼
  [pending]
     │
     ├── (venue requires invoice) ──► Invoice Sent ──► Payment Received ──► [paid]
     │
     └── (no invoice needed) ──────────────────────► Payment Received ──► [paid]
```

## Venue Payment Settings

Each venue stores:
- `payment_method`: How they typically pay
- `requires_invoice`: Whether you need to invoice them
- `has_w9`: For tax reporting purposes

### Payment Methods

- Cash (paid night-of)
- Check (pick up or mailed)
- Venmo
- Cash App
- PayPal
- Direct Deposit (corporate, slower)

## Show Payment Fields

| Field | Type | Description |
|-------|------|-------------|
| pay_amount | REAL | Amount for this gig |
| payment_status | TEXT | pending, paid |
| payment_received_date | DATE | When paid |
| invoice_sent | BOOLEAN | If invoice was sent |
| invoice_sent_date | DATE | When invoice sent |

## Quick Actions

### Mark as Paid (`p` key)

```
┌─ Mark Paid ───────────────────────────────────────────────┐
│                                                           │
│ Show: The Blue Note - Jan 25, 2025                       │
│ Amount: $200                                              │
│                                                           │
│ Payment received on: [2025-01-30    ]                    │
│                                                           │
│                        [Confirm]  [Cancel]                │
└───────────────────────────────────────────────────────────┘
```

### Mark Invoice Sent (`i` key)

Only available when venue has `requires_invoice = true`:

```
┌─ Invoice Sent ────────────────────────────────────────────┐
│                                                           │
│ Show: Corporate Gig - Jan 20, 2025                       │
│ Venue: Acme Corp (requires invoice)                      │
│                                                           │
│ Invoice sent on: [2025-01-21    ]                        │
│                                                           │
│                        [Confirm]  [Cancel]                │
└───────────────────────────────────────────────────────────┘
```

## Payment Status Display

| Condition | Display | Color |
|-----------|---------|-------|
| Future show | "pending" | gray |
| Past, < 30 days unpaid | "UNPAID (Xd)" | yellow |
| Past, >= 30 days unpaid | "OVERDUE (Xd)" | red |
| Paid | "paid" | green |
| Needs invoice, not sent | "needs invoice" | orange |

### Status Calculation Rules

**Days calculation**: Uses calendar days from show date to today (not exact hours).

```
Days unpaid = (today's date) - (show date)
```

**Example**: Show on Jan 1, today is Jan 31 → "OVERDUE (30d)"

**Priority when multiple conditions apply**:
1. If `payment_status = "paid"` → always show "paid" (green)
2. If show is in future → always show "pending" (gray)
3. If `needs_invoice` AND show is past → show "needs invoice" (orange)
4. Otherwise → show "UNPAID" or "OVERDUE" based on days

**Note**: "needs invoice" only shows if venue has `requires_invoice = true` AND invoice hasn't been sent AND show is in the past AND payment is pending.

See: [Algorithms](./13-algorithms.md) for exact calculation functions

## Dashboard Stats

- **Unpaid balance**: Sum of pay_amount where status = pending and date is past
- **Awaiting invoices**: Count of completed shows needing invoice

## Related Features

- [Data Model](./01-data-model.md)
- [Shows](./03-shows.md)
- [Smart Reports](./08-smart-reports.md)
- [Tax Reports](./09-tax-reports.md)
- [Algorithms](./13-algorithms.md)
