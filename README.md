# Gigsly

A TUI application for musicians to track gigs, venues, payments, and booking outreach.

## Features

- **Show Calendar** - Month and agenda views of upcoming and past gigs
- **Venue Management** - Track contacts, booking windows, and payment preferences
- **Payment Tracking** - Know what's owed, send invoice reminders, mark paid
- **Smart Reports** - Priority-scored action items: get paid, book shows, stay in touch
- **Recurring Gigs** - Set up weekly, monthly, or custom repeating shows
- **Tax Reports** - Year-end income and mileage summaries
- **Calendar Sync** - Import/export via ICS files for Google Calendar, etc.

## Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/gigsly.git
cd gigsly

# Install with UV
uv sync

# Run
uv run gigsly
```

## Quick Start

```bash
# Launch the TUI
gigsly

# Generate action report (no TUI)
gigsly report

# Tax summary for a year
gigsly tax 2025

# Export shows to calendar
gigsly export-calendar
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `d` | Dashboard |
| `v` | Venues |
| `s` | Shows |
| `c` | Calendar |
| `r` | Report |
| `n` | New (context-dependent) |
| `?` | Help |
| `q` | Quit / Back |

## Documentation

- [Tech Stack](docs/TECH_STACK.md)
- [Task List](docs/TASK_LIST.md)
- [Full Design](docs/plans/2025-01-30-gigsly-design.md)

## Requirements

- Python 3.14+
- UV package manager

## License

MIT
