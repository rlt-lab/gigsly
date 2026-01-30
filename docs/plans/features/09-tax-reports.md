# Tax Reports

## Overview

Generate year-end summaries for tax purposes, including income breakdown by W-9 status and mileage deduction calculations.

## Access

- **CLI**: `gigsly tax 2025` or `gigsly tax` (defaults to current year)
- **TUI**: Settings screen → [Export Tax Report] button (generates to file)

## W-9 Tracking

Venues have a `has_w9` boolean field:
- **Yes**: You've submitted a W-9, expect a 1099 if paid > $600
- **No**: Cash/informal payments, self-reported income

This separation helps reconcile against 1099s at tax time.

## Report Output

```
═══════════════════════════════════════════════════════════
                    2025 TAX SUMMARY
═══════════════════════════════════════════════════════════

─── INCOME (W-9 Venues) ───────────────────────────────────
Expect 1099 forms from these venues if paid > $600

  The Blue Note              12 shows      $2,400.00
  Ryman Auditorium            6 shows      $2,100.00
  Acme Corp                   4 shows      $2,000.00
  ─────────────────────────────────────────────────────
  Subtotal (W-9)             22 shows      $6,500.00

─── INCOME (No W-9) ───────────────────────────────────────
Self-reported income - no 1099 expected

  Exit/In                     8 shows        $600.00
  3rd & Lindsley             10 shows        $875.00
  House Concerts              5 shows        $375.00
  ─────────────────────────────────────────────────────
  Subtotal (No W-9)          23 shows      $1,850.00

═══════════════════════════════════════════════════════════
  TOTAL INCOME               45 shows      $8,350.00
═══════════════════════════════════════════════════════════

─── MILEAGE ───────────────────────────────────────────────

  Total miles driven:                        2,847 mi
  IRS standard rate (2025):                  $0.70/mi
  ─────────────────────────────────────────────────────
  Deduction value:                         $1,992.90

─── SUMMARY ───────────────────────────────────────────────

  Gross Income:              $8,350.00
  Mileage Deduction:        -$1,992.90
  ─────────────────────────────────────────────────────
  Net (before other deductions): $6,357.10

  Unique venues played:           12
  Total shows:                    45

═══════════════════════════════════════════════════════════
```

## Mileage Calculation

For each show:
- Look up venue's `mileage_one_way`
- Multiply by 2 for round trip
- Sum all shows in the tax year

The IRS rate is configurable in settings (updates annually).

## CLI Options

```bash
# Current year
gigsly tax

# Specific year
gigsly tax 2024

# Export to file
gigsly tax 2025 --output tax-2025.txt

# JSON format for import to spreadsheet
gigsly tax 2025 --format json
```

## Configuration

In `~/.gigsly/config.toml`:

```toml
[tax]
# IRS standard mileage rate (update annually)
irs_mileage_rate_2024 = 0.67
irs_mileage_rate_2025 = 0.70
```

## Related Features

- [Venues](./02-venues.md) - W-9 tracking
- [Shows](./03-shows.md) - Income data
- [Data Model](./01-data-model.md) - Mileage storage
