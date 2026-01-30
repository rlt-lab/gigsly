# Gigsly Documentation

A TUI application for musicians to track gigs, venues, payments, and booking outreach.

## Quick Links

- [Tech Stack](./TECH_STACK.md) - Technology choices and rationale
- [Task List](./TASK_LIST.md) - Implementation checklist
- [Design Overview](./plans/2025-01-30-gigsly-design.md) - Full design document

## Feature Specifications

| Feature | Description |
|---------|-------------|
| [Data Model](./plans/features/01-data-model.md) | Database schema and relationships |
| [Venues](./plans/features/02-venues.md) | Venue management and contact info |
| [Shows](./plans/features/03-shows.md) | Gig tracking and entry |
| [Calendar](./plans/features/04-calendar.md) | Month and agenda views |
| [Recurring Gigs](./plans/features/05-recurring-gigs.md) | Repeating show patterns |
| [Payments](./plans/features/06-payments.md) | Payment tracking and invoicing |
| [Contact Tracking](./plans/features/07-contact-tracking.md) | Venue outreach logging |
| [Smart Reports](./plans/features/08-smart-reports.md) | Priority-scored action items |
| [Tax Reports](./plans/features/09-tax-reports.md) | Year-end income and mileage |
| [ICS Calendar](./plans/features/10-ics-calendar.md) | Import/export calendar files |
| [Settings & Backup](./plans/features/11-settings-backup.md) | Configuration and data management |

## Project Structure

```
gigsly/
├── cli.py              # Entry point, Click commands
├── app.py              # Main Textual application
├── db/
│   ├── models.py       # SQLAlchemy models
│   ├── database.py     # Connection, migrations
│   └── queries.py      # Common queries
├── screens/
│   ├── dashboard.py
│   ├── calendar.py
│   ├── venues.py
│   ├── shows.py
│   └── report.py
├── widgets/            # Reusable UI components
└── config.py           # User settings
```
