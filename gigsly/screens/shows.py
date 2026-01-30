"""Shows screen for Gigsly TUI."""

from datetime import date
from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
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

from gigsly.db.models import Show, Venue
from gigsly.db.session import get_session
from gigsly.db import crud
from gigsly.screens.base import BaseScreen
from gigsly.widgets.confirm import confirm
from gigsly.widgets.flash import FlashMessage
from gigsly.widgets.datepicker import DatePicker


class ShowsScreen(BaseScreen):
    """Main shows list screen."""

    TITLE = "Shows"

    CSS = """
    ShowsScreen {
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
        width: 16;
    }

    .show-list {
        height: 1fr;
    }

    .show-list DataTable {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("n", "new_show", "New Show"),
        Binding("N", "new_show_venue", "New + Venue"),
        Binding("enter", "view_show", "View", show=False),
        Binding("p", "mark_paid", "Mark Paid"),
        Binding("i", "mark_invoice", "Invoice Sent"),
        Binding("d", "delete_show", "Delete"),
        Binding("slash", "focus_search", "Search"),
        Binding("f", "filter_menu", "Filter"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("v", "go_to_venues", "Venues"),
        Binding("c", "go_to_calendar", "Calendar"),
        Binding("q", "go_back", "Back"),
    ]

    def __init__(self, venue_id: Optional[int] = None) -> None:
        super().__init__()
        self._shows: list[Show] = []
        self._filter = "upcoming"
        self._search_query = ""
        self._venue_id = venue_id  # Filter to specific venue

    def compose(self) -> ComposeResult:
        yield Header()
        yield from self.compose_flash()

        with Horizontal(classes="search-bar"):
            yield Input(placeholder="Search shows...", id="search-input")
            yield Button("Filter: Upcoming", id="filter-btn")

        with Container(classes="show-list"):
            yield DataTable(id="shows-table")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the table and load data."""
        table = self.query_one("#shows-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("Date", "Venue", "Pay", "Status")

        if self._venue_id:
            with get_session() as session:
                venue = crud.get_venue(session, self._venue_id)
                if venue:
                    self.title = f"Shows - {venue.name}"

        self._load_shows()

    def _load_shows(self) -> None:
        """Load shows from database and populate table."""
        table = self.query_one("#shows-table", DataTable)
        table.clear()

        with get_session() as session:
            # Get shows based on filter
            if self._filter == "upcoming":
                shows = crud.get_upcoming_shows(session)
            elif self._filter == "past":
                shows = crud.get_past_shows(session)
            elif self._filter == "unpaid":
                shows = crud.get_unpaid_shows(session)
            elif self._filter == "needs_invoice":
                shows = crud.get_shows_needing_invoice(session)
            else:
                shows = crud.get_all_shows(session)

            # Filter by venue if specified
            if self._venue_id:
                shows = [s for s in shows if s.venue_id == self._venue_id]

            # Apply search
            if self._search_query:
                q = self._search_query.lower()
                shows = [
                    s for s in shows
                    if q in s.display_name.lower()
                    or q in str(s.date)
                    or (s.notes and q in s.notes.lower())
                ]

            self._shows = shows

            if not shows:
                table.add_row("No shows", "", "", "", key="empty")
                return

            today = date.today()
            for show in shows:
                # Format date
                date_str = show.date.strftime("%Y-%m-%d")
                if show.date.weekday() < 5:
                    day_name = show.date.strftime("%a")
                    date_str = f"{day_name} {date_str}"

                # Format status
                if show.is_cancelled:
                    status = "[dim]cancelled[/dim]"
                elif show.payment_status == "paid":
                    status = "[green]paid[/green]"
                elif show.date < today:
                    days = (today - show.date).days
                    if days >= 30:
                        status = f"[red]OVERDUE ({days}d)[/red]"
                    else:
                        status = f"[yellow]UNPAID ({days}d)[/yellow]"
                else:
                    status = "pending"

                # Format pay
                pay_str = f"${show.pay_amount:,.0f}" if show.pay_amount else "-"

                table.add_row(
                    date_str,
                    show.display_name,
                    pay_str,
                    status,
                    key=str(show.id),
                )

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self._search_query = event.value
            self._load_shows()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search-input", Input).focus()

    def action_filter_menu(self) -> None:
        """Cycle through filter options."""
        filters = ["upcoming", "past", "all", "unpaid", "needs_invoice"]
        current_idx = filters.index(self._filter) if self._filter in filters else 0
        next_idx = (current_idx + 1) % len(filters)
        self._filter = filters[next_idx]

        labels = {
            "upcoming": "Upcoming",
            "past": "Past",
            "all": "All",
            "unpaid": "Unpaid",
            "needs_invoice": "Needs Invoice",
        }
        self.query_one("#filter-btn", Button).label = f"Filter: {labels[self._filter]}"
        self._load_shows()

    def action_new_show(self) -> None:
        """Open form to create new show."""
        self.app.push_screen(ShowFormScreen(venue_id=self._venue_id), self._on_show_saved)

    def action_new_show_venue(self) -> None:
        """Open form to create new show with new venue."""
        self.app.push_screen(ShowFormScreen(create_venue=True), self._on_show_saved)

    def _on_show_saved(self, show_id: Optional[int]) -> None:
        """Handle show save callback."""
        if show_id:
            self.flash_success("Show added")
            self._load_shows()

    def action_view_show(self) -> None:
        """View the selected show."""
        show = self._get_selected_show()
        if show:
            self.app.push_screen(ShowDetailScreen(show.id), self._on_detail_closed)

    def _on_detail_closed(self, result) -> None:
        """Refresh list when detail screen closes."""
        self._load_shows()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        if event.row_key and str(event.row_key.value) != "empty":
            self.app.push_screen(
                ShowDetailScreen(int(event.row_key.value)),
                self._on_detail_closed,
            )

    def _get_selected_show(self) -> Optional[Show]:
        """Get the currently selected show."""
        table = self.query_one("#shows-table", DataTable)
        if table.cursor_row is None:
            return None
        try:
            row_key = table.get_row_at(table.cursor_row)
            if row_key:
                key = table.get_row_key(row_key)
                if key and str(key) != "empty":
                    show_id = int(key.value)
                    return next((s for s in self._shows if s.id == show_id), None)
        except Exception:
            pass
        return None

    async def action_mark_paid(self) -> None:
        """Mark selected show as paid."""
        show = self._get_selected_show()
        if not show:
            return

        if show.payment_status == "paid":
            self.flash_warning("Already marked as paid")
            return

        # Show date picker for payment date
        self.app.push_screen(
            PaymentDateScreen(show.id),
            self._on_payment_marked,
        )

    def _on_payment_marked(self, result) -> None:
        """Handle payment marked callback."""
        if result:
            self.flash_success(f"Marked as paid")
            self._load_shows()

    async def action_mark_invoice(self) -> None:
        """Mark invoice as sent for selected show."""
        show = self._get_selected_show()
        if not show:
            return

        if show.invoice_sent:
            self.flash_warning("Invoice already marked as sent")
            return

        with get_session() as session:
            crud.mark_invoice_sent(session, show.id, date.today())
            session.commit()

        self.flash_success("Invoice marked as sent")
        self._load_shows()

    async def action_delete_show(self) -> None:
        """Delete selected show."""
        show = self._get_selected_show()
        if not show:
            return

        msg = f"Delete show at {show.display_name} on {show.date}?"
        if show.pay_amount:
            msg += f"\n\nPay: ${show.pay_amount:,.0f} ({show.payment_status})"

        confirmed = await confirm(
            self.app,
            title="Delete Show",
            message=msg,
            confirm_label="Delete",
            danger=True,
        )

        if confirmed:
            with get_session() as session:
                crud.delete_show(session, show.id)
                session.commit()
            self.flash_success("Show deleted")
            self._load_shows()

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        table = self.query_one("#shows-table", DataTable)
        table.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up."""
        table = self.query_one("#shows-table", DataTable)
        table.action_cursor_up()

    def action_go_to_venues(self) -> None:
        """Navigate to venues."""
        from gigsly.screens.venues import VenuesScreen
        self.app.switch_screen(VenuesScreen())

    def action_go_to_calendar(self) -> None:
        """Navigate to calendar."""
        from gigsly.screens.calendar import CalendarScreen
        self.app.switch_screen(CalendarScreen())


class ShowDetailScreen(BaseScreen):
    """Show detail view screen."""

    CSS = """
    ShowDetailScreen {
        layout: vertical;
    }

    .detail-container {
        padding: 1 2;
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("e", "edit_show", "Edit"),
        Binding("p", "mark_paid", "Mark Paid"),
        Binding("i", "mark_invoice", "Invoice Sent"),
        Binding("d", "delete_show", "Delete"),
        Binding("q", "go_back", "Back"),
    ]

    def __init__(self, show_id: int) -> None:
        super().__init__()
        self.show_id = show_id
        self._show: Optional[Show] = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield from self.compose_flash()

        with VerticalScroll(classes="detail-container"):
            yield Static("Loading...", id="show-content")

        yield Footer()

    def on_mount(self) -> None:
        """Load show data."""
        self._load_show()

    def _load_show(self) -> None:
        """Load show from database."""
        with get_session() as session:
            self._show = crud.get_show_with_venue(session, self.show_id)
            if not self._show:
                self.flash_error("Show not found")
                self.app.pop_screen()
                return

            self._update_display()

    def _update_display(self) -> None:
        """Update the display with show data."""
        if not self._show:
            return

        show = self._show
        today = date.today()

        # Format status
        if show.is_cancelled:
            status = "Cancelled"
        elif show.payment_status == "paid":
            status = f"Paid ({show.payment_received_date})"
        elif show.date < today:
            days = (today - show.date).days
            if days >= 30:
                status = f"OVERDUE ({days} days)"
            else:
                status = f"Unpaid ({days} days)"
        else:
            status = "Pending"

        # Check invoice requirement
        requires_invoice = show.venue.requires_invoice if show.venue else False
        invoice_section = ""
        if requires_invoice:
            invoice_status = f"Sent ({show.invoice_sent_date})" if show.invoice_sent else "Not sent"
            invoice_section = f"""
─── Payment ───────────────────────────────────────

[bold]Invoice Required:[/bold] Yes
[bold]Invoice Sent:[/bold]     {invoice_status}
"""

        # Recurring info
        recurring_section = ""
        if show.recurring_gig:
            recurring_section = f"""
─── Recurring ─────────────────────────────────────

[bold]Part of:[/bold] {show.recurring_gig.pattern_type.replace("_", " ").title()} at {show.display_name}
"""

        content = f"""[bold]Show: {show.date.strftime('%B %d, %Y')}[/bold]

[bold]Venue:[/bold]  {show.display_name}
[bold]Date:[/bold]   {show.date.strftime('%A, %B %d, %Y')}
[bold]Pay:[/bold]    {f"${show.pay_amount:,.0f}" if show.pay_amount else "-"}
[bold]Status:[/bold] {status}
{invoice_section}{recurring_section}
─── Notes ─────────────────────────────────────────

{show.notes or "(none)"}
"""

        self.query_one("#show-content", Static).update(content)
        self.title = f"Show: {show.date}"

    def action_edit_show(self) -> None:
        """Edit this show."""
        self.app.push_screen(
            ShowFormScreen(show_id=self.show_id),
            self._on_edit_complete,
        )

    def _on_edit_complete(self, show_id: Optional[int]) -> None:
        """Handle edit completion."""
        if show_id:
            self.flash_success("Show updated")
            self._load_show()

    async def action_mark_paid(self) -> None:
        """Mark this show as paid."""
        if not self._show:
            return

        if self._show.payment_status == "paid":
            self.flash_warning("Already marked as paid")
            return

        self.app.push_screen(
            PaymentDateScreen(self.show_id),
            self._on_payment_marked,
        )

    def _on_payment_marked(self, result) -> None:
        """Handle payment marked callback."""
        if result:
            self.flash_success("Marked as paid")
            self._load_show()

    async def action_mark_invoice(self) -> None:
        """Mark invoice as sent."""
        if not self._show:
            return

        if self._show.invoice_sent:
            self.flash_warning("Invoice already marked as sent")
            return

        with get_session() as session:
            crud.mark_invoice_sent(session, self.show_id, date.today())
            session.commit()

        self.flash_success("Invoice marked as sent")
        self._load_show()

    async def action_delete_show(self) -> None:
        """Delete this show."""
        if not self._show:
            return

        confirmed = await confirm(
            self.app,
            title="Delete Show",
            message=f"Delete show at {self._show.display_name} on {self._show.date}?",
            confirm_label="Delete",
            danger=True,
        )

        if confirmed:
            with get_session() as session:
                crud.delete_show(session, self.show_id)
                session.commit()
            self.flash_success("Show deleted")
            self.app.pop_screen()


class ShowFormScreen(ModalScreen):
    """Modal form for creating/editing shows."""

    CSS = """
    ShowFormScreen {
        align: center middle;
    }

    ShowFormScreen > Vertical {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    ShowFormScreen .form-title {
        text-style: bold;
        margin-bottom: 1;
        text-align: center;
    }

    ShowFormScreen .form-row {
        height: auto;
        margin-bottom: 1;
    }

    ShowFormScreen .form-label {
        width: 12;
        padding-top: 1;
    }

    ShowFormScreen .form-input {
        width: 1fr;
    }

    ShowFormScreen .button-bar {
        height: 3;
        align: right middle;
        margin-top: 1;
    }

    ShowFormScreen Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    def __init__(
        self,
        show_id: Optional[int] = None,
        venue_id: Optional[int] = None,
        create_venue: bool = False,
    ) -> None:
        super().__init__()
        self.show_id = show_id
        self.venue_id = venue_id
        self.create_venue = create_venue
        self._show: Optional[Show] = None
        self._venues: list[Venue] = []

    def compose(self) -> ComposeResult:
        title = "Edit Show" if self.show_id else "New Show"
        if self.create_venue:
            title = "New Show + Venue"

        with Vertical():
            yield Label(title, classes="form-title")

            if self.create_venue:
                with Horizontal(classes="form-row"):
                    yield Label("Venue Name *", classes="form-label")
                    yield Input(id="venue_name", classes="form-input")

                with Horizontal(classes="form-row"):
                    yield Label("Location", classes="form-label")
                    yield Input(id="venue_location", classes="form-input", placeholder="City/Area")
            else:
                with Horizontal(classes="form-row"):
                    yield Label("Venue *", classes="form-label")
                    yield Select([], id="venue", prompt="Select venue...")

            with Horizontal(classes="form-row"):
                yield Label("Date *", classes="form-label")
                yield Input(id="date", classes="form-input", placeholder="YYYY-MM-DD")

            with Horizontal(classes="form-row"):
                yield Label("Pay", classes="form-label")
                yield Input(id="pay_amount", classes="form-input", placeholder="e.g. 200")

            with Horizontal(classes="form-row"):
                yield Label("Notes", classes="form-label")
                yield Input(id="notes", classes="form-input")

            with Horizontal(classes="button-bar"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Save", variant="primary", id="save")

    def on_mount(self) -> None:
        """Load data for form."""
        # Load venues for dropdown
        if not self.create_venue:
            with get_session() as session:
                self._venues = crud.get_all_venues(session)
                venue_select = self.query_one("#venue", Select)
                venue_select.set_options(
                    [(v.name, v.id) for v in self._venues]
                )

                if self.venue_id:
                    venue_select.value = self.venue_id

        # Load existing show if editing
        if self.show_id:
            with get_session() as session:
                self._show = crud.get_show(session, self.show_id)
                if self._show:
                    self._populate_form()

        # Set default date
        if not self.show_id:
            # Default to tomorrow
            tomorrow = date.today()
            self.query_one("#date", Input).value = tomorrow.isoformat()

        # Focus first field
        if self.create_venue:
            self.query_one("#venue_name", Input).focus()
        else:
            self.query_one("#venue", Select).focus()

    def _populate_form(self) -> None:
        """Populate form with existing show data."""
        if not self._show:
            return

        s = self._show
        if s.venue_id and not self.create_venue:
            self.query_one("#venue", Select).value = s.venue_id

        self.query_one("#date", Input).value = s.date.isoformat()
        self.query_one("#pay_amount", Input).value = str(s.pay_amount) if s.pay_amount else ""
        self.query_one("#notes", Input).value = s.notes or ""

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle venue selection to prefill typical pay."""
        if event.select.id == "venue" and event.value and event.value != Select.BLANK:
            venue = next((v for v in self._venues if v.id == event.value), None)
            if venue and venue.typical_pay and not self.show_id:
                pay_input = self.query_one("#pay_amount", Input)
                if not pay_input.value:
                    pay_input.value = str(int(venue.typical_pay))

    def action_cancel(self) -> None:
        """Cancel and close."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            self._save_show()

    def action_save(self) -> None:
        """Save the show."""
        self._save_show()

    def _save_show(self) -> None:
        """Save show to database."""
        # Validate date
        date_str = self.query_one("#date", Input).value.strip()
        try:
            show_date = date.fromisoformat(date_str)
        except ValueError:
            self.app.bell()
            self.query_one("#date", Input).focus()
            return

        with get_session() as session:
            venue_id = None

            if self.create_venue:
                # Create new venue
                venue_name = self.query_one("#venue_name", Input).value.strip()
                if not venue_name:
                    self.app.bell()
                    self.query_one("#venue_name", Input).focus()
                    return

                venue_data = {"name": venue_name}
                location = self.query_one("#venue_location", Input).value.strip()
                if location:
                    venue_data["location"] = location

                venue = crud.create_venue(session, **venue_data)
                venue_id = venue.id
            else:
                venue_id = self.query_one("#venue", Select).value
                if not venue_id or venue_id == Select.BLANK:
                    self.app.bell()
                    return

            # Build show data
            data = {
                "venue_id": venue_id,
                "date": show_date,
            }

            pay_str = self.query_one("#pay_amount", Input).value.strip()
            if pay_str:
                try:
                    data["pay_amount"] = float(pay_str)
                except ValueError:
                    pass

            notes = self.query_one("#notes", Input).value.strip()
            if notes:
                data["notes"] = notes

            # Save to database
            if self.show_id:
                show = crud.update_show(session, self.show_id, **data)
            else:
                show = crud.create_show(session, **data)

            session.commit()
            self.dismiss(show.id if show else None)


class PaymentDateScreen(ModalScreen):
    """Modal for selecting payment date."""

    CSS = """
    PaymentDateScreen {
        align: center middle;
    }

    PaymentDateScreen > Vertical {
        width: 40;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    PaymentDateScreen .form-title {
        text-style: bold;
        margin-bottom: 1;
        text-align: center;
    }

    PaymentDateScreen .form-row {
        height: auto;
        margin-bottom: 1;
    }

    PaymentDateScreen .button-bar {
        height: 3;
        align: right middle;
        margin-top: 1;
    }

    PaymentDateScreen Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "save", "Save"),
    ]

    def __init__(self, show_id: int) -> None:
        super().__init__()
        self.show_id = show_id

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Mark as Paid", classes="form-title")

            with Horizontal(classes="form-row"):
                yield Label("Payment Date:")
                yield Input(id="payment_date", placeholder="YYYY-MM-DD")

            with Horizontal(classes="button-bar"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Save", variant="primary", id="save")

    def on_mount(self) -> None:
        """Set default date to today."""
        self.query_one("#payment_date", Input).value = date.today().isoformat()
        self.query_one("#payment_date", Input).focus()

    def action_cancel(self) -> None:
        """Cancel and close."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            self._save()

    def action_save(self) -> None:
        """Save payment."""
        self._save()

    def _save(self) -> None:
        """Mark show as paid."""
        date_str = self.query_one("#payment_date", Input).value.strip()
        try:
            payment_date = date.fromisoformat(date_str)
        except ValueError:
            self.app.bell()
            return

        with get_session() as session:
            crud.mark_show_paid(session, self.show_id, payment_date)
            session.commit()

        self.dismiss(True)
