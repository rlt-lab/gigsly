# Settings & Backup

## Overview

Configure application behavior and manage data backups.

## Data Location

All Gigsly data lives in `~/.gigsly/`:

```
~/.gigsly/
├── gigsly.db           # SQLite database
├── config.toml         # User settings
├── exports/            # ICS and JSON exports
└── backups/            # Database backups
```

## Settings Screen

Access via `Ctrl+,` key or main menu → Settings:

```
┌─ Settings ────────────────────────────────────────────────┐
│                                                           │
│ ─── Thresholds ──────────────────────────────────────────│
│                                                           │
│ Payment overdue after:     [30    ] days                 │
│ Low show count threshold:  [2     ] shows                │
│ Contact reminder after:    [60    ] days                 │
│ Booking window alert:      [7     ] days before          │
│                                                           │
│ ─── Tax & Mileage ───────────────────────────────────────│
│                                                           │
│ Home address:              [_______________________]     │
│   (Used for mileage calculations)                        │
│ IRS mileage rate (2025):   [0.70  ] per mile            │
│                                                           │
│ ─── Data ────────────────────────────────────────────────│
│                                                           │
│ Database location: ~/.gigsly/gigsly.db                   │
│ Database size: 156 KB                                     │
│ Total venues: 12                                          │
│ Total shows: 47                                           │
│                                                           │
│ [Backup Now]  [Restore from Backup]  [Import Calendar]   │
│ [Export JSON]  [Export Tax Report]                       │
│                                                           │
│                                    [Save]  [Cancel]       │
└───────────────────────────────────────────────────────────┘
```

## Configuration File

`~/.gigsly/config.toml`:

```toml
[thresholds]
payment_overdue_days = 30
low_show_count = 2
contact_reminder_days = 60
booking_window_alert_days = 7

[tax]
home_address = ""
irs_mileage_rate_2024 = 0.67
irs_mileage_rate_2025 = 0.70

[display]
# Future: theme settings, date format preferences
```

## Backup

### CLI Commands

```bash
# Create backup
gigsly backup
# → Creates ~/.gigsly/backups/gigsly-backup-2025-01-30-143022.json

# Create backup to specific location
gigsly backup --output ~/Desktop/gigsly-backup.json

# List available backups
gigsly backup --list
```

### Backup Format

JSON export of all data:

```json
{
  "version": "1.0",
  "exported_at": "2025-01-30T14:30:22Z",
  "venues": [
    {
      "id": 1,
      "name": "The Blue Note",
      "location": "Nashville",
      ...
    }
  ],
  "shows": [...],
  "recurring_gigs": [...],
  "contact_logs": [...]
}
```

## Restore

### CLI Command

```bash
# Restore from backup
gigsly restore ~/.gigsly/backups/gigsly-backup-2025-01-30.json

# Preview restore without applying
gigsly restore backup.json --dry-run
```

### Restore Behavior

1. Parse backup file
2. Validate format and version
3. **Prompt for confirmation**: "This will replace all existing data. Continue?"
4. Clear existing tables
5. Import all records
6. Report summary

### Merge Option

```bash
# Merge backup with existing data (skip duplicates)
gigsly restore backup.json --merge
```

**Merge behavior:**
- Venues: Match by name (case-insensitive). If exists, skip. If not, import.
- Shows: Match by venue_id + date. If exists, skip. If not, import.
- RecurringGigs: Match by venue_id + pattern_type + day_of_week. If exists, skip.
- ContactLogs: Always import (append to history).

**Merge preview:**
```
$ gigsly restore backup.json --merge --dry-run

Merge Preview:
  Venues:       3 new, 9 existing (skip)
  Shows:        12 new, 35 existing (skip)
  Recurring:    1 new, 2 existing (skip)
  Contacts:     24 to import

Run without --dry-run to apply.
```

**TUI access**: Settings screen → [Restore from Backup] button shows:

```
┌─ Restore from Backup ─────────────────────────────────────┐
│                                                           │
│ File: [~/.gigsly/backups/backup-2025-01-15.json] [Browse] │
│                                                           │
│ Mode:                                                     │
│ ○ Replace all data (destructive)                         │
│ ● Merge with existing (keeps current data)               │
│                                                           │
│ ⚠ Replace will delete all current data first.           │
│                                                           │
│                        [Restore]  [Cancel]                │
└───────────────────────────────────────────────────────────┘
```

## JSON Export (for spreadsheets)

```bash
# Export to JSON for analysis
gigsly export-json

# Export specific data
gigsly export-json --venues
gigsly export-json --shows --year 2025
```

## First-Run Setup

On first launch:

1. Check if `~/.gigsly/` exists
2. If not:
   - Create directory structure
   - Initialize empty database
   - Create default config.toml
   - Display welcome message

```
┌─ Welcome to Gigsly ───────────────────────────────────────┐
│                                                           │
│ Gigsly helps you track gigs, venues, and payments.       │
│                                                           │
│ Get started:                                              │
│   • Press 'v' to add your first venue                    │
│   • Press 'n' to add a show                              │
│   • Press 'r' to see what needs your attention           │
│   • Press '?' for help anytime                           │
│                                                           │
│                                    [Let's Go!]            │
└───────────────────────────────────────────────────────────┘
```

## Related Features

- [Smart Reports](./08-smart-reports.md) - Uses threshold settings
- [Tax Reports](./09-tax-reports.md) - Uses IRS rate setting
- [ICS Calendar](./10-ics-calendar.md) - Export functionality
