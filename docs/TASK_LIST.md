# Gigsly Implementation Task List

## Phase 1: Foundation

- [x] **1.1** Set up project structure and dependencies
  - Create package structure (`gigsly/`, `db/`, `screens/`, `widgets/`)
  - Add dependencies to `pyproject.toml`
  - Configure UV environment
  - See: [Tech Stack](./TECH_STACK.md)

- [x] **1.2** Implement data model and database
  - Create SQLAlchemy models (Venue, Show, ContactLog, RecurringGig)
  - Include `venue_name_snapshot` field on Show for soft-delete support
  - Set up database initialization and migrations
  - Write basic CRUD operations
  - Implement validation rules per [Data Model](./plans/features/01-data-model.md) invariants
  - See: [Data Model](./plans/features/01-data-model.md), [Algorithms](./plans/features/13-algorithms.md)

- [x] **1.3** Create CLI entry point
  - Set up Click commands:
    - `gigsly` - launch TUI
    - `gigsly report` - smart report to terminal
    - `gigsly tax [year]` - tax report to terminal
    - `gigsly backup` / `gigsly restore` - data backup/restore
    - `gigsly export-calendar` / `gigsly import-calendar` - ICS sync
    - `gigsly export-json` - JSON data export
  - Initialize Textual app launcher
  - Handle first-run setup (create ~/.gigsly/)

- [x] **1.4** Create shared widget library
  - Flash message component (success, warning, error with auto-dismiss)
  - Confirmation dialog component (with optional text input for "DELETE")
  - Date picker widget
  - Dropdown/select widget
  - See: Referenced in [Shows](./plans/features/03-shows.md), [Venues](./plans/features/02-venues.md)

## Phase 2: Core Screens

- [x] **2.1** Build Venues screen
  - Searchable/filterable venue list (`/` search, `f` filter menu)
  - Venue detail view with all fields and stats (total shows, total earned)
  - Add venue form (`n` key)
  - Edit venue functionality (`e` key)
  - Contact history view (`h` key)
  - See: [Venues](./plans/features/02-venues.md)
  - **Depends on**: 1.2, 1.4 (data model, shared widgets)

- [x] **2.1a** Implement venue deletion with soft-delete
  - Delete venue with typed "DELETE" confirmation (`d` key)
  - Preserve venue name on past shows (denormalized)
  - Cancel future shows and deactivate recurring gigs
  - See: [Venues](./plans/features/02-venues.md), [Algorithms](./plans/features/13-algorithms.md)
  - **Depends on**: 2.1

- [x] **2.2a** Build Shows list and filters
  - Show list with columns: Date, Venue, Pay, Status
  - Filter menu (`f` key): Upcoming, Past, All, Unpaid, Needs Invoice
  - Search functionality (`/` key)
  - See: [Shows](./plans/features/03-shows.md)
  - **Depends on**: 2.1 (venue selection requires venues)

- [x] **2.2b** Build Show add/edit flows
  - Quick add show (`n` - existing venue dropdown)
  - Add show with new venue (`N` - creates minimal venue)
  - Edit show details (`e` key)
  - Flash messages for confirmations
  - See: [Shows](./plans/features/03-shows.md)
  - **Depends on**: 2.2a, 1.4 (list exists, shared widgets)

- [x] **2.2c** Implement payment actions
  - Mark paid (`p`) with date picker modal
  - Mark invoice sent (`i`) - only if venue requires invoice
  - Delete show with confirmation (`d` key)
  - See: [Shows](./plans/features/03-shows.md), [Payments](./plans/features/06-payments.md)
  - **Depends on**: 2.2b

- [x] **2.3** Build Calendar screen
  - Month view with show markers (color-coded by payment status)
  - Agenda view (chronological list with filters)
  - Toggle between views (`Tab` or `m`/`a`)
  - Navigate months (`←`/`→`), jump to today (`t`)
  - See: [Calendar](./plans/features/04-calendar.md)
  - **Depends on**: 2.2a (calendar displays shows)

- [x] **2.4** Build Dashboard screen
  - Quick stats (upcoming shows, YTD earnings, unpaid balance)
  - Next 14 days show list (max 5 with overflow count)
  - Needs attention section with priority-ordered action items
  - Navigation shortcuts to other screens
  - Manual refresh (`Ctrl+R`)
  - See: [Dashboard](./plans/features/12-dashboard.md), [Algorithms](./plans/features/13-algorithms.md)
  - **Depends on**: 2.2c, 2.3 (reuses show list, needs payment status)

- [x] **2.5** Implement first-run onboarding
  - "Getting Started" guide for new users (empty state)
  - Welcome modal on first launch
  - Quick-add prompts to create first venue
  - See: [Dashboard](./plans/features/12-dashboard.md)
  - **Depends on**: 2.4

## Phase 3: Advanced Features

- [ ] **3.1a** Implement recurring gig patterns
  - RecurringGig creation form with pattern selection
  - Support all 5 pattern types: weekly, biweekly, monthly_date, monthly_ordinal, custom
  - Pattern field validation per [Algorithms](./plans/features/13-algorithms.md)
  - See: [Recurring Gigs](./plans/features/05-recurring-gigs.md)
  - **Depends on**: 2.2b (show creation flow exists)

- [ ] **3.1b** Implement instance generation
  - Auto-generate instances for next 3 months on app launch
  - Idempotent generation (skip existing dates)
  - Handle edge cases: fifth weekday, month-end dates
  - Manual regeneration trigger (`Ctrl+R`)
  - See: [Recurring Gigs](./plans/features/05-recurring-gigs.md), [Algorithms](./plans/features/13-algorithms.md)
  - **Depends on**: 3.1a

- [ ] **3.1c** Implement recurring instance editing
  - Edit series vs edit single instance dialog
  - "Apply to: this only / this+future / all" options
  - Skip/cancel individual occurrences
  - Delete series with cascade options
  - See: [Recurring Gigs](./plans/features/05-recurring-gigs.md)
  - **Depends on**: 3.1b

- [ ] **3.2** Implement payment tracking enhancements
  - Payment status display with days count (UNPAID/OVERDUE)
  - Invoice workflow for venues requiring invoices
  - Payment overdue detection per [Algorithms](./plans/features/13-algorithms.md)
  - Unpaid balance calculation
  - See: [Payments](./plans/features/06-payments.md)
  - **Depends on**: 2.2c (basic payment actions exist)

- [ ] **3.3** Implement contact tracking
  - Contact log entry form (`c` from venue detail)
  - Outcome-based effects (awaiting response suppression, follow-up priority)
  - Last contacted display on venues list (color-coded)
  - Contact history view (`h` from venue detail)
  - Follow-up date reminders
  - See: [Contact Tracking](./plans/features/07-contact-tracking.md), [Algorithms](./plans/features/13-algorithms.md)
  - **Depends on**: 2.1 (venue detail screen exists)

- [ ] **3.4** Implement booking window alerts
  - "Days until window" calculation per [Algorithms](./plans/features/13-algorithms.md)
  - Dashboard alerts for windows opening soon
  - Color-coded urgency (yellow/orange/red)
  - See: [Contact Tracking](./plans/features/07-contact-tracking.md)
  - **Depends on**: 3.3, 2.4 (contact tracking, dashboard exist)

## Phase 4: Reports

- [ ] **4.1** Build Smart Report
  - Priority scoring algorithm per [Algorithms](./plans/features/13-algorithms.md)
  - "Get Paid" section (unpaid, invoices)
  - "Book Shows" section (booking windows, low counts)
  - "Stay in Touch" section (contact reminders)
  - Section assignment based on primary condition
  - Color-coded priority (red/yellow/green)
  - Section jump keys (`1`/`2`/`3`)
  - Manual refresh (`Ctrl+R`)
  - CLI command: `gigsly report`
  - See: [Smart Reports](./plans/features/08-smart-reports.md), [Algorithms](./plans/features/13-algorithms.md)
  - **Depends on**: 3.2, 3.3, 3.4 (uses payment, contact, booking window data)

- [ ] **4.2** Build Tax Report
  - W-9 tracking on venues
  - Income summary by W-9 status (1099 expected vs self-reported)
  - Mileage totals and deduction calculation
  - Round-trip mileage (venue mileage × 2)
  - Year filter (defaults to current year)
  - CLI command: `gigsly tax <year>`
  - See: [Tax Reports](./plans/features/09-tax-reports.md)
  - **Depends on**: 2.2c (needs shows with payment data)

## Phase 5: Import/Export

- [ ] **5.1** Implement ICS calendar support
  - Export shows to .ics file (TUI: Calendar `e` key, CLI: `gigsly export-calendar`)
  - Import events from .ics file (TUI: Settings button, CLI: `gigsly import-calendar`)
  - Match imported events to venues by name (case-insensitive)
  - Handle recurring events (RRULE) - convert to RecurringGig or individual shows
  - See: [ICS Calendar](./plans/features/10-ics-calendar.md)
  - **Depends on**: 3.1c (needs full recurring gig support for RRULE import)

- [ ] **5.2** Implement backup/restore
  - JSON export of all data with version field
  - JSON import with replace or merge modes
  - Replace: wipe and restore
  - Merge: skip duplicate venues (by name), append contact logs, update existing shows
  - TUI: Settings screen buttons
  - CLI commands: `gigsly backup`, `gigsly restore [--merge]`
  - Backup directory: `~/.gigsly/backups/` with timestamps
  - See: [Settings & Backup](./plans/features/11-settings-backup.md)
  - **Depends on**: 1.2 (full data model)

## Phase 6: Polish

- [ ] **6.1** Settings screen
  - Configurable thresholds (overdue days, low show count, contact reminder days, booking window alert days)
  - Home address setting (for mileage base)
  - IRS mileage rate (yearly values)
  - Data stats display (database size, counts)
  - See: [Settings & Backup](./plans/features/11-settings-backup.md)
  - **Depends on**: 5.2 (backup buttons on settings screen)

- [ ] **6.2** Help overlay
  - Keyboard shortcut help (`?` key)
  - Context-sensitive: shows current screen name and relevant shortcuts
  - See: [Keyboard Shortcuts](./plans/features/00-keyboard-shortcuts.md)
  - **Depends on**: All screens complete

- [ ] **6.3** Testing and documentation
  - Unit tests for business logic (pytest) - especially [Algorithms](./plans/features/13-algorithms.md)
  - Integration tests for database (pytest + fixtures)
  - TUI tests using Textual's pilot testing framework
  - Test coverage target: 80% for business logic
  - Update README with usage instructions
  - See: [Testing Strategy](#testing-strategy)

---

## Implementation Order Rationale

1. **Foundation first** (1.1-1.4) - Can't build anything without the data layer and shared widgets
2. **Venues before Shows** (2.1) - Shows depend on venues existing
3. **Shows list before add/edit** (2.2a → 2.2b → 2.2c) - Build list view, then creation flows, then payment actions
4. **Calendar after Shows** (2.3) - Calendar displays show data
5. **Dashboard after payment actions** (2.4) - Needs payment status for "needs attention" section
6. **First-run after Dashboard** (2.5) - Empty state handling for new users
7. **Recurring patterns before generation** (3.1a → 3.1b → 3.1c) - Define patterns, then generate, then edit
8. **Contact tracking before booking alerts** (3.3 → 3.4) - Alerts depend on contact outcome effects
9. **Smart Report after all Phase 3** (4.1) - Uses payment, contact, and booking window data
10. **Tax Report can parallel Smart Report** (4.2) - Only needs shows with payment data
11. **ICS Import after recurring** (5.1) - RRULE support requires full recurring gig implementation
12. **Backup/Restore early in Phase 5** (5.2) - Doesn't depend on advanced features
13. **Settings screen after backup** (6.1) - Contains backup buttons
14. **Help overlay last** (6.2) - Needs all screens complete for context-sensitive help

### Dependency Graph (Critical Path)

```
1.2 → 2.1 → 2.2a → 2.2b → 2.2c → 2.4 → 4.1
                ↘         ↘
                 2.3      3.1a → 3.1b → 3.1c → 5.1
                          ↘
                           3.2 → 4.1
                           3.3 → 3.4 → 4.1
```

---

## Testing Strategy

### Test Framework
- **pytest** for all tests
- **pytest-asyncio** for async database operations
- **Textual pilot** for TUI component testing

### Test Categories

| Category | Location | Coverage Target |
|----------|----------|-----------------|
| Unit tests | `tests/unit/` | Business logic, scoring algorithms |
| Database tests | `tests/db/` | CRUD operations, migrations |
| TUI tests | `tests/tui/` | Screen navigation, keyboard shortcuts |
| CLI tests | `tests/cli/` | Command parsing, output format |

### Fixtures

Standard test fixtures in `tests/conftest.py`:
- `test_db`: In-memory SQLite database
- `sample_venues`: 3 venues with varying attributes
- `sample_shows`: Shows covering past, future, paid, unpaid
- `sample_recurring`: Weekly and monthly recurring gigs

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=gigsly --cov-report=html

# Specific category
uv run pytest tests/unit/
```
