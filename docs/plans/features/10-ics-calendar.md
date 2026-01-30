# ICS Calendar Import/Export

## Overview

Exchange show data with external calendars (Google Calendar, Apple Calendar, Outlook) using the standard ICS file format.

## Export Shows

### CLI Command

```bash
# Export all upcoming shows
gigsly export-calendar

# Export specific date range
gigsly export-calendar --start 2025-02-01 --end 2025-12-31

# Export to specific file
gigsly export-calendar --output ~/Desktop/gigs.ics
```

### Default Behavior

- Exports to `~/.gigsly/exports/gigsly-shows-YYYY-MM-DD.ics`
- Includes all shows from today forward
- Past shows excluded by default (use `--include-past` to include)

### ICS Event Format

Each show becomes a calendar event:

```ics
BEGIN:VEVENT
UID:gigsly-show-123@gigsly.local
DTSTART:20250201
DTEND:20250201
SUMMARY:Gig: The Blue Note
LOCATION:123 Music Row, Nashville, TN 37203
DESCRIPTION:Pay: $200\nStatus: pending
CATEGORIES:GIGSLY
END:VEVENT
```

**Fields mapped:**
- `SUMMARY`: "Gig: {venue_name}"
- `DTSTART/DTEND`: Show date (all-day event)
- `LOCATION`: Venue address
- `DESCRIPTION`: Pay amount, status, notes
- `CATEGORIES`: "GIGSLY" tag for identification

## Import Shows

### CLI Command

```bash
# Import from file
gigsly import-calendar ~/Downloads/calendar.ics

# Preview without importing
gigsly import-calendar ~/Downloads/calendar.ics --dry-run
```

### Import Logic

1. Parse ICS file for events
2. For each event:
   - Check if SUMMARY matches pattern "Gig: {venue_name}" (Gigsly export)
   - Or look for "GIGSLY" category
   - If neither, prompt: "Import '{event_title}' as a show?"
3. Match venue by name:
   - If venue exists, link to it
   - If not, create new venue (minimal info)
4. Create show record
5. Skip duplicates (same venue + same date)

### Import Preview

```
$ gigsly import-calendar gigs.ics --dry-run

Found 5 events in calendar.ics:

  ✓ Feb 1, 2025: "Gig: The Blue Note"
    → Will link to existing venue: The Blue Note

  ✓ Feb 8, 2025: "Ryman Show"
    → Will create new venue: Ryman Show

  ⚠ Feb 14, 2025: "Valentine's Dinner"
    → No venue match, skip? [y/N]

  ✗ Feb 1, 2025: "Gig: The Blue Note"
    → Duplicate, already exists

Would import 2 shows, create 1 venue. Run without --dry-run to import.
```

### Conflict Handling

| Scenario | Behavior |
|----------|----------|
| Same venue + same date exists | Skip (duplicate) |
| Venue name matches existing | Link to existing venue |
| Venue name not found | Create new venue |
| Event has no location | Use event title as venue name |

### Recurring Events (RRULE)

ICS files may contain recurring events with `RRULE` definitions.

**Import behavior:**
- If the ICS event has an `RRULE`, offer to create a RecurringGig in Gigsly
- Parse supported patterns: WEEKLY, MONTHLY (by day or ordinal)
- Unsupported patterns (complex RRULE): Import as individual shows for each occurrence

```
┌─ Recurring Event Detected ────────────────────────────────┐
│                                                           │
│ "Weekly at The Blue Note" repeats every Saturday         │
│                                                           │
│ How would you like to import this?                       │
│                                                           │
│ ○ Create recurring gig (will auto-generate future shows) │
│ ● Import as individual shows (12 occurrences found)      │
│                                                           │
│                        [Import]  [Cancel]                 │
└───────────────────────────────────────────────────────────┘
```

**Supported RRULE patterns:**
| ICS Pattern | Gigsly Pattern |
|-------------|----------------|
| `FREQ=WEEKLY;BYDAY=SA` | Weekly (Saturday) |
| `FREQ=WEEKLY;INTERVAL=2;BYDAY=WE` | Bi-weekly (Wednesday) |
| `FREQ=MONTHLY;BYMONTHDAY=15` | Monthly (15th) |
| `FREQ=MONTHLY;BYDAY=1SA` | Monthly (First Saturday) |

**Unsupported patterns** (import as individual shows):
- Complex RRULE with multiple BYDAY values
- YEARLY frequency
- COUNT or UNTIL with many occurrences (>50)

## Google Calendar Workflow

### Export to Google Calendar

1. Run `gigsly export-calendar`
2. Open Google Calendar
3. Settings → Import & Export → Import
4. Select the .ics file
5. Choose calendar to import to

### Import from Google Calendar

1. Open Google Calendar
2. Settings → Import & Export → Export
3. Download .ics file
4. Run `gigsly import-calendar ~/Downloads/calendar.ics`

## TUI Access

### Export (Calendar screen → `e` key)

```
┌─ Export Calendar ─────────────────────────────────────────┐
│                                                           │
│ Export shows to ICS file for use in other calendars.     │
│                                                           │
│ Range: [Upcoming only     ▼]                             │
│        • Upcoming only                                    │
│        • Next 3 months                                    │
│        • This year                                        │
│        • All shows                                        │
│                                                           │
│ File: ~/.gigsly/exports/gigsly-shows-2025-01-30.ics      │
│                                                           │
│                        [Export]  [Cancel]                 │
└───────────────────────────────────────────────────────────┘
```

### Import (Settings screen → [Import Calendar] button)

```
┌─ Import Calendar ─────────────────────────────────────────┐
│                                                           │
│ Import shows from an ICS file.                           │
│                                                           │
│ File: [~/Downloads/calendar.ics          ] [Browse...]   │
│                                                           │
│ ─── Preview ─────────────────────────────────────────────│
│                                                           │
│ ✓ Feb 1, 2025: "Gig: The Blue Note"                     │
│   → Will link to: The Blue Note                          │
│                                                           │
│ ✓ Feb 8, 2025: "Ryman Show"                             │
│   → Will create venue: Ryman Show                        │
│                                                           │
│ ⚠ Feb 14, 2025: "Valentine's Dinner"                    │
│   → No venue match  [Import anyway] [Skip]               │
│                                                           │
│ ✗ Feb 1, 2025: "Gig: The Blue Note"                     │
│   → Duplicate, will skip                                 │
│                                                           │
│ Summary: 2 shows to import, 1 venue to create            │
│                                                           │
│                        [Import]  [Cancel]                 │
└───────────────────────────────────────────────────────────┘
```

## Related Features

- [Shows](./03-shows.md)
- [Calendar](./04-calendar.md)
- [Settings & Backup](./11-settings-backup.md)
