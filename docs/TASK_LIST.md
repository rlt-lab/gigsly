# Gigsly Implementation Task List

## Phase 1: Foundation

- [ ] **1.1** Set up project structure and dependencies
  - Create package structure (`gigsly/`, `db/`, `screens/`, `widgets/`)
  - Add dependencies to `pyproject.toml`
  - Configure UV environment
  - See: [Tech Stack](./TECH_STACK.md)

- [ ] **1.2** Implement data model and database
  - Create SQLAlchemy models (Venue, Show, ContactLog, RecurringGig)
  - Set up database initialization and migrations
  - Write basic CRUD operations
  - See: [Data Model](./plans/features/01-data-model.md)

- [ ] **1.3** Create CLI entry point
  - Set up Click commands (`gigsly`, `gigsly report`, `gigsly backup`)
  - Initialize Textual app launcher
  - Handle first-run setup (create ~/.gigsly/)

## Phase 2: Core Screens

- [ ] **2.1** Build Venues screen
  - Searchable/filterable venue list
  - Venue detail view with all fields
  - Add venue form (`n` key)
  - Edit venue functionality
  - See: [Venues](./plans/features/02-venues.md)

- [ ] **2.2** Build Shows screen
  - Show list with filters (upcoming, past, unpaid)
  - Quick add show (`n` - existing venue)
  - Add show with new venue (`N`)
  - Mark paid / mark invoice sent actions
  - See: [Shows](./plans/features/03-shows.md)

- [ ] **2.3** Build Calendar screen
  - Month view with show markers
  - Agenda view (chronological list)
  - Toggle between views (`Tab` or `m`/`a`)
  - Navigate months (`←`/`→`)
  - See: [Calendar](./plans/features/04-calendar.md)

- [ ] **2.4** Build Dashboard screen
  - Quick stats (upcoming shows, YTD earnings, unpaid balance)
  - Mini calendar (next 2 weeks)
  - Action needed badge
  - Navigation shortcuts

## Phase 3: Advanced Features

- [ ] **3.1** Implement recurring gigs
  - Recurrence pattern selection UI
  - Auto-generation of future show instances
  - Edit series vs edit instance logic
  - Skip/cancel individual occurrences
  - See: [Recurring Gigs](./plans/features/05-recurring-gigs.md)

- [ ] **3.2** Implement payment tracking
  - Payment status workflow (pending → paid)
  - Invoice tracking for venues that require it
  - Payment method on venues
  - Payment overdue detection
  - See: [Payments](./plans/features/06-payments.md)

- [ ] **3.3** Implement contact tracking
  - Contact log entry form
  - Last contacted display on venues
  - Booking window alerts
  - See: [Contact Tracking](./plans/features/07-contact-tracking.md)

## Phase 4: Reports

- [ ] **4.1** Build Smart Report
  - Priority scoring algorithm
  - "Get Paid" section (unpaid, invoices)
  - "Book Shows" section (booking windows, low counts)
  - "Stay in Touch" section (contact reminders)
  - CLI command: `gigsly report`
  - See: [Smart Reports](./plans/features/08-smart-reports.md)

- [ ] **4.2** Build Tax Report
  - W-9 tracking on venues
  - Income summary by W-9 status
  - Mileage totals and deduction calculation
  - CLI command: `gigsly tax <year>`
  - See: [Tax Reports](./plans/features/09-tax-reports.md)

## Phase 5: Import/Export

- [ ] **5.1** Implement ICS calendar support
  - Export shows to .ics file
  - Import events from .ics file
  - Match imported events to venues
  - CLI commands: `gigsly export-calendar`, `gigsly import-calendar`
  - See: [ICS Calendar](./plans/features/10-ics-calendar.md)

- [ ] **5.2** Implement backup/restore
  - JSON export of all data
  - JSON import with conflict handling
  - CLI commands: `gigsly backup`, `gigsly restore`
  - See: [Settings & Backup](./plans/features/11-settings-backup.md)

## Phase 6: Polish

- [ ] **6.1** Settings screen
  - Configurable thresholds
  - Home address setting
  - IRS mileage rate

- [ ] **6.2** Help and onboarding
  - Keyboard shortcut help (`?`)
  - First-run welcome/tutorial

- [ ] **6.3** Testing and documentation
  - Unit tests for business logic
  - Integration tests for database
  - Update README with usage instructions

---

## Implementation Order Rationale

1. **Foundation first** - Can't build anything without the data layer
2. **Venues before Shows** - Shows depend on venues existing
3. **Calendar after Shows** - Calendar displays show data
4. **Recurring gigs after basic shows** - Builds on show creation
5. **Reports after core data** - Need data to report on
6. **Import/Export last** - Nice-to-have, not blocking core functionality
