"""Venues screen for Gigsly TUI."""

from datetime import date
from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Rule,
    Select,
    Static,
)

from gigsly.db.models import PaymentMethod, Venue
from gigsly.db.session import get_session
from gigsly.db import crud
from gigsly.screens.base import BaseScreen
from gigsly.widgets.confirm import confirm_delete
from gigsly.widgets.flash import FlashMessage


class VenuesScreen(BaseScreen):
    """Main venues list screen."""

    TITLE = "Venues"

    CSS = """
    VenuesScreen {
        layout: vertical;
    }

    .search-bar {
        height: 3;
        padding: 0 1;
    }

    .search-bar Input {
        width: 1fr;
    }

    .search-bar Button {
        width: 12;
    }

    .venue-list {
        height: 1fr;
    }

    .venue-list DataTable {
        height: 100%;
    }

    .empty-state {
        width: 100%;
        height: 100%;
        align: center middle;
        content-align: center middle;
    }

    .empty-state Static {
        text-align: center;
        padding: 2;
    }
    """

    BINDINGS = [
        Binding("n", "new_venue", "New Venue"),
        Binding("enter", "view_venue", "View", show=False),
        Binding("slash", "focus_search", "Search"),
        Binding("f", "filter_menu", "Filter"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("d", "go_to_dashboard", "Dashboard"),
        Binding("s", "go_to_shows", "Shows"),
        Binding("c", "go_to_calendar", "Calendar"),
        Binding("q", "go_back", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._venues: list[Venue] = []
        self._filter = "all"
        self._search_query = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield from self.compose_flash()

        with Horizontal(classes="search-bar"):
            yield Input(placeholder="Search venues...", id="search-input")
            yield Button("Filter: All", id="filter-btn")

        with Container(classes="venue-list"):
            yield DataTable(id="venues-table")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the table and load data."""
        table = self.query_one("#venues-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("Name", "Location", "Last Contact", "Upcoming")
        self._load_venues()

    def _load_venues(self) -> None:
        """Load venues from database and populate table."""
        table = self.query_one("#venues-table", DataTable)
        table.clear()

        with get_session() as session:
            if self._search_query:
                self._venues = crud.search_venues(session, self._search_query)
            else:
                self._venues = crud.get_all_venues(session)

            # Apply filter
            filtered = self._apply_filter(self._venues, session)

            if not filtered:
                table.add_row("No venues", "", "", "", key="empty")
                return

            for venue in filtered:
                # Get stats
                upcoming_count = len([s for s in venue.shows if s.date >= date.today() and not s.is_cancelled])

                # Get last contact
                last_contact = ""
                if venue.contact_logs:
                    latest = max(venue.contact_logs, key=lambda c: c.contacted_at)
                    days_ago = (date.today() - latest.contacted_at.date()).days
                    last_contact = f"{latest.contacted_at.date()} ({days_ago}d ago)"

                table.add_row(
                    venue.name,
                    venue.location or "",
                    last_contact,
                    f"{upcoming_count} shows" if upcoming_count else "-",
                    key=str(venue.id),
                )

    def _apply_filter(self, venues: list[Venue], session) -> list[Venue]:
        """Apply the current filter to venues."""
        if self._filter == "all":
            return venues

        today = date.today()

        if self._filter == "upcoming":
            return [v for v in venues if any(s.date >= today and not s.is_cancelled for s in v.shows)]
        elif self._filter == "no_upcoming":
            return [v for v in venues if not any(s.date >= today and not s.is_cancelled for s in v.shows)]
        elif self._filter == "needs_contact":
            result = []
            for v in venues:
                if not v.contact_logs:
                    result.append(v)
                else:
                    latest = max(v.contact_logs, key=lambda c: c.contacted_at)
                    if (today - latest.contacted_at.date()).days >= 60:
                        result.append(v)
            return result

        return venues

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self._search_query = event.value
            self._load_venues()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search-input", Input).focus()

    def action_filter_menu(self) -> None:
        """Show filter options."""
        filters = ["all", "upcoming", "no_upcoming", "needs_contact"]
        current_idx = filters.index(self._filter) if self._filter in filters else 0
        next_idx = (current_idx + 1) % len(filters)
        self._filter = filters[next_idx]

        labels = {
            "all": "All",
            "upcoming": "Has Upcoming",
            "no_upcoming": "No Upcoming",
            "needs_contact": "Needs Contact",
        }
        self.query_one("#filter-btn", Button).label = f"Filter: {labels[self._filter]}"
        self._load_venues()

    def action_new_venue(self) -> None:
        """Open form to create new venue."""
        self.app.push_screen(VenueFormScreen(), self._on_venue_saved)

    def _on_venue_saved(self, venue_id: Optional[int]) -> None:
        """Handle venue save callback."""
        if venue_id:
            self.flash_success("Venue created successfully")
            self._load_venues()

    def action_view_venue(self) -> None:
        """View the selected venue."""
        table = self.query_one("#venues-table", DataTable)
        if table.cursor_row is not None:
            row_key = table.get_row_at(table.cursor_row)
            if row_key:
                venue_id = table.get_row_key(row_key)
                if venue_id and venue_id != "empty":
                    self.app.push_screen(
                        VenueDetailScreen(int(venue_id)),
                        self._on_detail_closed,
                    )

    def _on_detail_closed(self, result) -> None:
        """Refresh list when detail screen closes."""
        self._load_venues()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        if event.row_key and str(event.row_key.value) != "empty":
            self.app.push_screen(
                VenueDetailScreen(int(event.row_key.value)),
                self._on_detail_closed,
            )

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        table = self.query_one("#venues-table", DataTable)
        table.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up."""
        table = self.query_one("#venues-table", DataTable)
        table.action_cursor_up()

    def action_go_to_dashboard(self) -> None:
        """Navigate to dashboard."""
        from gigsly.screens.dashboard import DashboardScreen
        self.app.switch_screen(DashboardScreen())

    def action_go_to_shows(self) -> None:
        """Navigate to shows."""
        from gigsly.screens.shows import ShowsScreen
        self.app.switch_screen(ShowsScreen())

    def action_go_to_calendar(self) -> None:
        """Navigate to calendar."""
        from gigsly.screens.calendar import CalendarScreen
        self.app.switch_screen(CalendarScreen())


class VenueDetailScreen(BaseScreen):
    """Venue detail view screen."""

    CSS = """
    VenueDetailScreen {
        layout: vertical;
    }

    .detail-container {
        padding: 1 2;
        height: 1fr;
    }

    .section-title {
        text-style: bold;
        margin-top: 1;
        margin-bottom: 0;
    }

    .field-row {
        height: auto;
    }

    .field-label {
        width: 16;
        text-style: bold;
    }

    .field-value {
        width: 1fr;
    }

    .stats-row {
        height: 3;
        margin-top: 1;
    }

    .stat-box {
        width: 1fr;
        height: 3;
        border: solid $primary;
        content-align: center middle;
        text-align: center;
    }
    """

    BINDINGS = [
        Binding("e", "edit_venue", "Edit"),
        Binding("d", "delete_venue", "Delete"),
        Binding("c", "log_contact", "Log Contact"),
        Binding("s", "view_shows", "Shows"),
        Binding("h", "view_history", "History"),
        Binding("q", "go_back", "Back"),
    ]

    def __init__(self, venue_id: int) -> None:
        super().__init__()
        self.venue_id = venue_id
        self._venue: Optional[Venue] = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield from self.compose_flash()

        with VerticalScroll(classes="detail-container"):
            yield Static("Loading...", id="venue-content")

        yield Footer()

    def on_mount(self) -> None:
        """Load venue data."""
        self._load_venue()

    def _load_venue(self) -> None:
        """Load venue from database."""
        with get_session() as session:
            self._venue = crud.get_venue_with_relations(session, self.venue_id)
            if not self._venue:
                self.flash_error("Venue not found")
                self.app.pop_screen()
                return

            self._update_display()

    def _update_display(self) -> None:
        """Update the display with venue data."""
        if not self._venue:
            return

        venue = self._venue
        today = date.today()

        # Calculate stats
        total_shows = len([s for s in venue.shows if not s.is_cancelled])
        total_earned = sum(s.pay_amount or 0 for s in venue.shows if s.payment_status == "paid")
        upcoming = len([s for s in venue.shows if s.date >= today and not s.is_cancelled])

        # Last contact
        last_contact = "Never"
        if venue.contact_logs:
            latest = max(venue.contact_logs, key=lambda c: c.contacted_at)
            days_ago = (today - latest.contacted_at.date()).days
            last_contact = f"{latest.contacted_at.date()} ({days_ago} days ago)"

        # Booking window
        booking_window = "-"
        if venue.booking_window_start and venue.booking_window_end:
            booking_window = f"{venue.booking_window_start} - {venue.booking_window_end} of each month"
        elif venue.booking_window_start:
            booking_window = f"{venue.booking_window_start} of each month"

        # Payment method display
        payment_method = venue.payment_method.replace("_", " ").title() if venue.payment_method else "-"

        content = f"""[bold]{venue.name}[/bold]

[bold]Location:[/bold]     {venue.location or "-"}
[bold]Address:[/bold]      {venue.address or "-"}
[bold]Contact:[/bold]      {venue.contact_name or "-"}
[bold]Email:[/bold]        {venue.contact_email or "-"}
[bold]Phone:[/bold]        {venue.contact_phone or "-"}

─── Booking ───────────────────────────────────────

[bold]Mileage:[/bold]      {f"{venue.mileage_one_way} miles ({venue.mileage_one_way * 2} mi round trip)" if venue.mileage_one_way else "-"}
[bold]Typical Pay:[/bold]  {f"${venue.typical_pay:,.0f}" if venue.typical_pay else "-"}
[bold]Payment:[/bold]      {payment_method}
[bold]Invoice Req:[/bold]  {"Yes" if venue.requires_invoice else "No"}
[bold]W-9 on File:[/bold]  {"Yes" if venue.has_w9 else "No"}
[bold]Books:[/bold]        {booking_window}

─── Stats ─────────────────────────────────────────

[bold]Total Shows:[/bold]  {total_shows}
[bold]Total Earned:[/bold] ${total_earned:,.0f}
[bold]Upcoming:[/bold]     {upcoming} shows
[bold]Last Contact:[/bold] {last_contact}

─── Notes ─────────────────────────────────────────

{venue.notes or "(none)"}
"""

        self.query_one("#venue-content", Static).update(content)
        self.title = venue.name

    def action_edit_venue(self) -> None:
        """Edit this venue."""
        self.app.push_screen(
            VenueFormScreen(venue_id=self.venue_id),
            self._on_edit_complete,
        )

    def _on_edit_complete(self, venue_id: Optional[int]) -> None:
        """Handle edit completion."""
        if venue_id:
            self.flash_success("Venue updated")
            self._load_venue()

    async def action_delete_venue(self) -> None:
        """Delete this venue."""
        if not self._venue:
            return

        # Build confirmation message
        today = date.today()
        past_shows = [s for s in self._venue.shows if s.date < today and not s.is_cancelled]
        future_shows = [s for s in self._venue.shows if s.date >= today and not s.is_cancelled]
        recurring = [g for g in self._venue.recurring_gigs if g.is_active]
        past_total = sum(s.pay_amount or 0 for s in past_shows if s.payment_status == "paid")

        msg = f'Delete "{self._venue.name}"?\n\n'
        if past_shows:
            msg += f"  - {len(past_shows)} past shows (${past_total:,.0f} total)\n"
        if future_shows:
            msg += f"  - {len(future_shows)} upcoming shows will be cancelled\n"
        if recurring:
            msg += f"  - {len(recurring)} active recurring gigs will end\n"
        msg += "\nPast shows will be preserved for tax records."

        confirmed = await confirm_delete(self.app, self._venue.name)
        if confirmed:
            with get_session() as session:
                crud.delete_venue(session, self.venue_id)
                session.commit()
            self.flash_success("Venue deleted")
            self.app.pop_screen()

    def action_log_contact(self) -> None:
        """Log a contact with this venue."""
        self.app.push_screen(
            ContactLogFormScreen(venue_id=self.venue_id),
            self._on_contact_logged,
        )

    def _on_contact_logged(self, result) -> None:
        """Handle contact log completion."""
        if result:
            self.flash_success("Contact logged")
            self._load_venue()

    def action_view_shows(self) -> None:
        """View shows at this venue."""
        from gigsly.screens.shows import ShowsScreen
        self.app.push_screen(ShowsScreen(venue_id=self.venue_id))

    def action_view_history(self) -> None:
        """View contact history."""
        self.app.push_screen(ContactHistoryScreen(venue_id=self.venue_id))


class VenueFormScreen(ModalScreen):
    """Modal form for creating/editing venues."""

    CSS = """
    VenueFormScreen {
        align: center middle;
    }

    VenueFormScreen > Vertical {
        width: 70;
        max-height: 90%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    VenueFormScreen .form-title {
        text-style: bold;
        margin-bottom: 1;
        text-align: center;
    }

    VenueFormScreen .form-row {
        height: auto;
        margin-bottom: 1;
    }

    VenueFormScreen .form-label {
        width: 18;
        padding-top: 1;
    }

    VenueFormScreen .form-input {
        width: 1fr;
    }

    VenueFormScreen .checkbox-row {
        height: 3;
    }

    VenueFormScreen .button-bar {
        height: 3;
        align: right middle;
        margin-top: 1;
    }

    VenueFormScreen Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    def __init__(self, venue_id: Optional[int] = None) -> None:
        super().__init__()
        self.venue_id = venue_id
        self._venue: Optional[Venue] = None

    def compose(self) -> ComposeResult:
        title = "Edit Venue" if self.venue_id else "New Venue"

        with VerticalScroll():
            yield Label(title, classes="form-title")

            with Horizontal(classes="form-row"):
                yield Label("Name *", classes="form-label")
                yield Input(id="name", classes="form-input")

            with Horizontal(classes="form-row"):
                yield Label("Location", classes="form-label")
                yield Input(id="location", classes="form-input", placeholder="City/Area")

            with Horizontal(classes="form-row"):
                yield Label("Address", classes="form-label")
                yield Input(id="address", classes="form-input")

            yield Rule()

            with Horizontal(classes="form-row"):
                yield Label("Contact Name", classes="form-label")
                yield Input(id="contact_name", classes="form-input")

            with Horizontal(classes="form-row"):
                yield Label("Email", classes="form-label")
                yield Input(id="contact_email", classes="form-input")

            with Horizontal(classes="form-row"):
                yield Label("Phone", classes="form-label")
                yield Input(id="contact_phone", classes="form-input")

            yield Rule()

            with Horizontal(classes="form-row"):
                yield Label("Mileage (one-way)", classes="form-label")
                yield Input(id="mileage", classes="form-input", placeholder="e.g. 12")

            with Horizontal(classes="form-row"):
                yield Label("Typical Pay", classes="form-label")
                yield Input(id="typical_pay", classes="form-input", placeholder="e.g. 200")

            with Horizontal(classes="form-row"):
                yield Label("Payment Method", classes="form-label")
                yield Select(
                    [
                        ("Cash", "cash"),
                        ("Check", "check"),
                        ("Venmo", "venmo"),
                        ("CashApp", "cashapp"),
                        ("PayPal", "paypal"),
                        ("Direct Deposit", "direct_deposit"),
                    ],
                    id="payment_method",
                    allow_blank=True,
                    prompt="Select...",
                )

            with Horizontal(classes="checkbox-row"):
                yield Label("", classes="form-label")
                yield Checkbox("Requires Invoice", id="requires_invoice")

            with Horizontal(classes="checkbox-row"):
                yield Label("", classes="form-label")
                yield Checkbox("W-9 on File", id="has_w9")

            yield Rule()

            with Horizontal(classes="form-row"):
                yield Label("Booking Window", classes="form-label")
                with Horizontal():
                    yield Input(id="booking_start", placeholder="Start day", width=10)
                    yield Label(" to ")
                    yield Input(id="booking_end", placeholder="End day", width=10)

            with Horizontal(classes="form-row"):
                yield Label("Notes", classes="form-label")
                yield Input(id="notes", classes="form-input")

            with Horizontal(classes="button-bar"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Save", variant="primary", id="save")

    def on_mount(self) -> None:
        """Load existing venue data if editing."""
        if self.venue_id:
            with get_session() as session:
                self._venue = crud.get_venue(session, self.venue_id)
                if self._venue:
                    self._populate_form()
        self.query_one("#name", Input).focus()

    def _populate_form(self) -> None:
        """Populate form with existing venue data."""
        if not self._venue:
            return

        v = self._venue
        self.query_one("#name", Input).value = v.name or ""
        self.query_one("#location", Input).value = v.location or ""
        self.query_one("#address", Input).value = v.address or ""
        self.query_one("#contact_name", Input).value = v.contact_name or ""
        self.query_one("#contact_email", Input).value = v.contact_email or ""
        self.query_one("#contact_phone", Input).value = v.contact_phone or ""
        self.query_one("#mileage", Input).value = str(v.mileage_one_way) if v.mileage_one_way else ""
        self.query_one("#typical_pay", Input).value = str(v.typical_pay) if v.typical_pay else ""

        if v.payment_method:
            self.query_one("#payment_method", Select).value = v.payment_method

        self.query_one("#requires_invoice", Checkbox).value = v.requires_invoice
        self.query_one("#has_w9", Checkbox).value = v.has_w9
        self.query_one("#booking_start", Input).value = str(v.booking_window_start) if v.booking_window_start else ""
        self.query_one("#booking_end", Input).value = str(v.booking_window_end) if v.booking_window_end else ""
        self.query_one("#notes", Input).value = v.notes or ""

    def action_cancel(self) -> None:
        """Cancel and close."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            self._save_venue()

    def action_save(self) -> None:
        """Save the venue."""
        self._save_venue()

    def _save_venue(self) -> None:
        """Save venue to database."""
        name = self.query_one("#name", Input).value.strip()
        if not name:
            self.app.bell()
            self.query_one("#name", Input).focus()
            return

        # Gather form data
        data = {
            "name": name,
            "location": self.query_one("#location", Input).value.strip() or None,
            "address": self.query_one("#address", Input).value.strip() or None,
            "contact_name": self.query_one("#contact_name", Input).value.strip() or None,
            "contact_email": self.query_one("#contact_email", Input).value.strip() or None,
            "contact_phone": self.query_one("#contact_phone", Input).value.strip() or None,
            "requires_invoice": self.query_one("#requires_invoice", Checkbox).value,
            "has_w9": self.query_one("#has_w9", Checkbox).value,
            "notes": self.query_one("#notes", Input).value.strip() or None,
        }

        # Parse numeric fields
        mileage = self.query_one("#mileage", Input).value.strip()
        if mileage:
            try:
                data["mileage_one_way"] = float(mileage)
            except ValueError:
                pass

        typical_pay = self.query_one("#typical_pay", Input).value.strip()
        if typical_pay:
            try:
                data["typical_pay"] = float(typical_pay)
            except ValueError:
                pass

        payment_method = self.query_one("#payment_method", Select).value
        if payment_method and payment_method != Select.BLANK:
            data["payment_method"] = payment_method

        booking_start = self.query_one("#booking_start", Input).value.strip()
        if booking_start:
            try:
                data["booking_window_start"] = int(booking_start)
            except ValueError:
                pass

        booking_end = self.query_one("#booking_end", Input).value.strip()
        if booking_end:
            try:
                data["booking_window_end"] = int(booking_end)
            except ValueError:
                pass

        # Save to database
        with get_session() as session:
            if self.venue_id:
                venue = crud.update_venue(session, self.venue_id, **data)
            else:
                venue = crud.create_venue(session, **data)
            session.commit()
            self.dismiss(venue.id if venue else None)


class ContactLogFormScreen(ModalScreen):
    """Modal form for logging contacts."""

    CSS = """
    ContactLogFormScreen {
        align: center middle;
    }

    ContactLogFormScreen > Vertical {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    ContactLogFormScreen .form-title {
        text-style: bold;
        margin-bottom: 1;
        text-align: center;
    }

    ContactLogFormScreen .form-row {
        height: auto;
        margin-bottom: 1;
    }

    ContactLogFormScreen .form-label {
        width: 14;
        padding-top: 1;
    }

    ContactLogFormScreen .form-input {
        width: 1fr;
    }

    ContactLogFormScreen .button-bar {
        height: 3;
        align: right middle;
        margin-top: 1;
    }

    ContactLogFormScreen Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    def __init__(self, venue_id: int) -> None:
        super().__init__()
        self.venue_id = venue_id

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Log Contact", classes="form-title")

            with Horizontal(classes="form-row"):
                yield Label("Method *", classes="form-label")
                yield Select(
                    [
                        ("Email", "email"),
                        ("Phone", "phone"),
                        ("In Person", "in_person"),
                        ("Other", "other"),
                    ],
                    id="method",
                    value="email",
                )

            with Horizontal(classes="form-row"):
                yield Label("Outcome", classes="form-label")
                yield Select(
                    [
                        ("Booked", "booked"),
                        ("Declined", "declined"),
                        ("Awaiting Response", "awaiting_response"),
                        ("Follow-up Needed", "follow_up_needed"),
                        ("Other", "other"),
                    ],
                    id="outcome",
                    allow_blank=True,
                    prompt="Select...",
                )

            with Horizontal(classes="form-row"):
                yield Label("Follow-up Date", classes="form-label")
                yield Input(id="follow_up", classes="form-input", placeholder="YYYY-MM-DD")

            with Horizontal(classes="form-row"):
                yield Label("Notes", classes="form-label")
                yield Input(id="notes", classes="form-input")

            with Horizontal(classes="button-bar"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Save", variant="primary", id="save")

    def on_mount(self) -> None:
        """Focus method select."""
        self.query_one("#method", Select).focus()

    def action_cancel(self) -> None:
        """Cancel and close."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            self._save_contact()

    def action_save(self) -> None:
        """Save the contact log."""
        self._save_contact()

    def _save_contact(self) -> None:
        """Save contact log to database."""
        from datetime import datetime

        method = self.query_one("#method", Select).value
        if not method or method == Select.BLANK:
            self.app.bell()
            return

        data = {
            "venue_id": self.venue_id,
            "contacted_at": datetime.now(),
            "method": method,
        }

        outcome = self.query_one("#outcome", Select).value
        if outcome and outcome != Select.BLANK:
            data["outcome"] = outcome

        follow_up = self.query_one("#follow_up", Input).value.strip()
        if follow_up:
            try:
                data["follow_up_date"] = date.fromisoformat(follow_up)
            except ValueError:
                pass

        notes = self.query_one("#notes", Input).value.strip()
        if notes:
            data["notes"] = notes

        with get_session() as session:
            crud.create_contact_log(session, **data)
            session.commit()

        self.dismiss(True)


class ContactHistoryScreen(BaseScreen):
    """Contact history view for a venue."""

    CSS = """
    ContactHistoryScreen {
        layout: vertical;
    }

    .history-container {
        padding: 1 2;
        height: 1fr;
    }

    .history-entry {
        margin-bottom: 1;
        padding: 1;
        border: solid $primary-lighten-3;
    }

    .entry-header {
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("q", "go_back", "Back"),
    ]

    def __init__(self, venue_id: int) -> None:
        super().__init__()
        self.venue_id = venue_id

    def compose(self) -> ComposeResult:
        yield Header()

        with VerticalScroll(classes="history-container"):
            yield Static("Loading...", id="history-content")

        yield Footer()

    def on_mount(self) -> None:
        """Load contact history."""
        with get_session() as session:
            venue = crud.get_venue(session, self.venue_id)
            if not venue:
                self.query_one("#history-content", Static).update("Venue not found")
                return

            self.title = f"Contact History - {venue.name}"
            logs = crud.get_contact_logs_for_venue(session, self.venue_id)

            if not logs:
                self.query_one("#history-content", Static).update(
                    "No contact history.\n\nPress [c] from venue detail to log a contact."
                )
                return

            content = ""
            for log in logs:
                outcome_display = log.outcome.replace("_", " ").title() if log.outcome else "-"
                content += f"""[bold]{log.contacted_at.strftime('%Y-%m-%d %H:%M')}[/bold]
Method: {log.method.replace("_", " ").title()}
Outcome: {outcome_display}
{f"Follow-up: {log.follow_up_date}" if log.follow_up_date else ""}
{f"Notes: {log.notes}" if log.notes else ""}

"""

            self.query_one("#history-content", Static).update(content)
