# Gigsly Design Document

**Date**: January 30, 2025
**Status**: Approved

## Summary

Gigsly is a TUI application for musicians to track gigs, venues, payments, and booking outreach. The primary goal is surfacing actionable insights: what payments are overdue, which venues need invoices, and who to contact for more bookings.

## Goals

1. **Track shows** with dates, venues, and payment information
2. **Manage venues** with contact details, booking windows, and payment preferences
3. **Surface action items** through smart priority-scored reports
4. **Generate tax summaries** with income and mileage breakdowns
5. **Sync with external calendars** via ICS import/export

## Non-Goals (v1)

- Mobile app
- Real-time Google Calendar sync (ICS files only)
- Multi-user / sharing
- Financial projections or analytics

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI | Textual TUI | Keyboard efficiency, terminal aesthetic, SSH portable |
| Database | SQLite | Single file, no server, easy backup |
| ORM | SQLAlchemy | Type-safe, migrations, Python standard |
| CLI | Click | Clean syntax, integrates with Textual |
| Config | TOML | Human-readable, Python standard |
| Calendar | ICS files | No OAuth complexity, universal format |

See: [Tech Stack](../TECH_STACK.md)

## Data Model

Four main entities:

- **Venue**: Location with contact info, payment preferences, booking windows
- **Show**: Individual gig linked to a venue
- **RecurringGig**: Pattern for repeating shows
- **ContactLog**: Record of outreach to venues

See: [Data Model](./features/01-data-model.md)

## User Interface

### Navigation

| Key | Action |
|-----|--------|
| `d` | Dashboard |
| `v` | Venues |
| `s` | Shows |
| `c` | Calendar |
| `r` | Report |
| `?` | Help |
| `q` | Quit / Back |

### Screens

1. **Dashboard**: Quick stats, mini calendar, action count
2. **Venues**: Searchable list, detail view, contact logging
3. **Shows**: Filterable list, quick add, payment actions
4. **Calendar**: Month view + agenda view, color-coded by status
5. **Report**: Priority-scored action items grouped by category

See individual feature specs for detailed layouts.

## Key Workflows

### Adding a Show

**Quick add (`n`)**: Select venue → Enter date → Confirm pay → Done

**With new venue (`N`)**: Enter venue name → Enter location → Enter date → Enter pay → Done (venue created with minimal info)

### Smart Report

Venues scored 0-100 based on:
- Unpaid gigs (35 pts)
- Invoice pending (30 pts)
- Booking window approaching (20 pts)
- Low show count (10 pts)
- Days since contact (5 pts)

Report sections: Get Paid → Book Shows → Stay in Touch

### Recurring Gigs

Patterns: Weekly, Bi-weekly, Monthly (date), Monthly (ordinal), Custom interval

System auto-generates show instances for next 3 months. Individual instances can be edited or skipped without affecting the series.

### Tax Reports

Income grouped by W-9 status (helps reconcile 1099s). Mileage calculated from venue distances. IRS rate configurable.

## Feature Specifications

| Feature | Document |
|---------|----------|
| Data Model | [01-data-model.md](./features/01-data-model.md) |
| Venues | [02-venues.md](./features/02-venues.md) |
| Shows | [03-shows.md](./features/03-shows.md) |
| Calendar | [04-calendar.md](./features/04-calendar.md) |
| Recurring Gigs | [05-recurring-gigs.md](./features/05-recurring-gigs.md) |
| Payments | [06-payments.md](./features/06-payments.md) |
| Contact Tracking | [07-contact-tracking.md](./features/07-contact-tracking.md) |
| Smart Reports | [08-smart-reports.md](./features/08-smart-reports.md) |
| Tax Reports | [09-tax-reports.md](./features/09-tax-reports.md) |
| ICS Calendar | [10-ics-calendar.md](./features/10-ics-calendar.md) |
| Settings & Backup | [11-settings-backup.md](./features/11-settings-backup.md) |

## Implementation Plan

See: [Task List](../TASK_LIST.md)

**Phase 1**: Foundation (project structure, data model, CLI)
**Phase 2**: Core Screens (venues, shows, calendar, dashboard)
**Phase 3**: Advanced Features (recurring gigs, payments, contacts)
**Phase 4**: Reports (smart report, tax report)
**Phase 5**: Import/Export (ICS, backup/restore)
**Phase 6**: Polish (settings, help, testing)
