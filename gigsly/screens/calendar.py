"""Calendar screen for Gigsly TUI."""

import calendar
from datetime import date, timedelta
from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll, Grid
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    Static,
)

from gigsly.db.models import Show
from gigsly.db.session import get_session
from gigsly.db import crud
from gigsly.screens.base import BaseScreen
from gigsly.widgets.flash import FlashMessage


class CalendarScreen(BaseScreen):
    """Calendar screen with month and agenda views."""

    TITLE = "Calendar"

    CSS = """
    CalendarScreen {
        layout: vertical;
    }

    .calendar-header {
        height: 3;
        align: center middle;
        background: $primary-darken-2;
    }

    .calendar-header Button {
        min-width: 10;
    }

    .calendar-header .month-title {
        width: 1fr;
        text-align: center;
        text-style: bold;
    }

    .calendar-container {
        height: 1fr;
        padding: 1;
    }

    .month-view {
        height: 100%;
    }

    .week-header {
        height: 1;
        width: 100%;
    }

    .week-header Label {
        width: 10;
        text-align: center;
        text-style: bold;
    }

    .calendar-grid {
        height: 1fr;
        grid-size: 7;
        grid-gutter: 0;
    }

    .day-cell {
        height: 4;
        width: 10;
        border: solid $primary-lighten-3;
        padding: 0 1;
    }

    .day-cell.today {
        border: thick $accent;
    }

    .day-cell.has-show {
        background: $primary-darken-2;
    }

    .day-cell .day-number {
        text-style: bold;
    }

    .day-cell .show-marker {
        color: $primary;
    }

    .day-cell .show-marker.paid {
        color: $success;
    }

    .day-cell .show-marker.unpaid {
        color: $warning;
    }

    .agenda-view {
        height: 1fr;
    }

    .agenda-view DataTable {
        height: 100%;
    }

    .view-toggle {
        dock: bottom;
        height: 3;
        align: center middle;
    }
    """

    BINDINGS = [
        Binding("tab", "toggle_view", "Toggle View"),
        Binding("m", "month_view", "Month", show=False),
        Binding("a", "agenda_view", "Agenda", show=False),
        Binding("left", "prev_month", "Prev Month"),
        Binding("right", "next_month", "Next Month"),
        Binding("h", "prev_month", "Prev", show=False),
        Binding("l", "next_month", "Next", show=False),
        Binding("t", "go_today", "Today"),
        Binding("n", "new_show", "New Show"),
        Binding("N", "new_show_venue", "New + Venue"),
        Binding("enter", "view_day", "View"),
        Binding("f", "filter_menu", "Filter"),
        Binding("e", "export_ics", "Export"),
        Binding("v", "go_to_venues", "Venues"),
        Binding("s", "go_to_shows", "Shows"),
        Binding("q", "go_back", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._view = "month"  # "month" or "agenda"
        self._current_date = date.today()
        self._shows: dict[date, list[Show]] = {}
        self._filter = "upcoming"
        self._selected_day: Optional[date] = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield from self.compose_flash()

        with Horizontal(classes="calendar-header"):
            yield Button("◀", id="prev-btn")
            yield Static("", id="month-title", classes="month-title")
            yield Button("▶", id="next-btn")

        with Container(classes="calendar-container"):
            yield Container(id="view-container")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize calendar."""
        self._load_shows()
        self._render_view()

    def _load_shows(self) -> None:
        """Load shows for the current month."""
        # Get date range for current view
        if self._view == "month":
            year = self._current_date.year
            month = self._current_date.month
            _, last_day = calendar.monthrange(year, month)
            start = date(year, month, 1)
            end = date(year, month, last_day)
        else:
            # Agenda view - next 3 months
            start = date.today()
            end = start + timedelta(days=90)

        with get_session() as session:
            shows = crud.get_shows_in_range(session, start, end)

            # Apply filter for agenda view
            if self._view == "agenda":
                today = date.today()
                if self._filter == "upcoming":
                    shows = [s for s in shows if s.date >= today and not s.is_cancelled]
                elif self._filter == "past":
                    shows = [s for s in shows if s.date < today and not s.is_cancelled]
                elif self._filter == "this_month":
                    shows = [s for s in shows if s.date.month == today.month and s.date.year == today.year]

            # Group by date
            self._shows = {}
            for show in shows:
                if show.is_cancelled:
                    continue
                if show.date not in self._shows:
                    self._shows[show.date] = []
                self._shows[show.date].append(show)

    def _render_view(self) -> None:
        """Render the current view."""
        container = self.query_one("#view-container", Container)
        container.remove_children()

        # Update title
        month_name = self._current_date.strftime("%B %Y")
        self.query_one("#month-title", Static).update(month_name)

        if self._view == "month":
            self._render_month_view(container)
        else:
            self._render_agenda_view(container)

    def _render_month_view(self, container: Container) -> None:
        """Render month grid view."""
        year = self._current_date.year
        month = self._current_date.month
        today = date.today()

        # Create month grid
        cal = calendar.monthcalendar(year, month)

        content = "[bold]  Sun   Mon   Tue   Wed   Thu   Fri   Sat[/bold]\n"
        content += "─" * 49 + "\n"

        for week in cal:
            row = ""
            for day in week:
                if day == 0:
                    row += "      "
                else:
                    d = date(year, month, day)
                    shows = self._shows.get(d, [])

                    # Format day
                    if d == today:
                        day_str = f"[bold cyan]{day:>2}[/bold cyan]"
                    elif shows:
                        # Color based on payment status
                        all_paid = all(s.payment_status == "paid" for s in shows)
                        any_unpaid = any(s.payment_status == "pending" and s.date < today for s in shows)
                        if all_paid:
                            day_str = f"[green]{day:>2}*[/green]"
                        elif any_unpaid:
                            day_str = f"[yellow]{day:>2}*[/yellow]"
                        else:
                            day_str = f"[blue]{day:>2}*[/blue]"
                    else:
                        day_str = f"{day:>2} "

                    row += f" {day_str}  "

            content += row + "\n"

            # Show venue names for days with shows
            venue_row = ""
            for day in week:
                if day == 0:
                    venue_row += "      "
                else:
                    d = date(year, month, day)
                    shows = self._shows.get(d, [])
                    if shows:
                        name = shows[0].display_name[:5]
                        venue_row += f" {name:<5}"
                    else:
                        venue_row += "      "
            content += f"[dim]{venue_row}[/dim]\n"

        container.mount(Static(content, id="month-grid"))

    def _render_agenda_view(self, container: Container) -> None:
        """Render agenda list view."""
        table = DataTable(id="agenda-table")
        table.cursor_type = "row"
        table.add_columns("Date", "Venue", "Pay", "Status")

        today = date.today()

        # Get sorted list of shows
        all_shows = []
        for show_list in self._shows.values():
            all_shows.extend(show_list)
        all_shows.sort(key=lambda s: s.date)

        if not all_shows:
            container.mount(Static(
                "No shows in this time range.\n\nPress [n] to add a show.",
                id="empty-agenda",
            ))
            return

        current_month = None
        for show in all_shows:
            # Add month header
            show_month = show.date.strftime("%B %Y")
            if show_month != current_month:
                current_month = show_month
                table.add_row(f"── {show_month} ──", "", "", "", key=f"header-{show_month}")

            # Format date
            date_str = show.date.strftime("%a %d")

            # Format status
            if show.payment_status == "paid":
                status = "[green]paid[/green]"
            elif show.date < today:
                days = (today - show.date).days
                if days >= 30:
                    status = f"[red]OVERDUE ({days}d)[/red]"
                else:
                    status = f"[yellow]UNPAID ({days}d)[/yellow]"
            else:
                status = "pending"

            pay_str = f"${show.pay_amount:,.0f}" if show.pay_amount else "-"

            table.add_row(
                date_str,
                show.display_name,
                pay_str,
                status,
                key=str(show.id),
            )

        container.mount(table)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle navigation buttons."""
        if event.button.id == "prev-btn":
            self.action_prev_month()
        elif event.button.id == "next-btn":
            self.action_next_month()

    def action_toggle_view(self) -> None:
        """Toggle between month and agenda views."""
        self._view = "agenda" if self._view == "month" else "month"
        self._load_shows()
        self._render_view()

    def action_month_view(self) -> None:
        """Switch to month view."""
        if self._view != "month":
            self._view = "month"
            self._load_shows()
            self._render_view()

    def action_agenda_view(self) -> None:
        """Switch to agenda view."""
        if self._view != "agenda":
            self._view = "agenda"
            self._load_shows()
            self._render_view()

    def action_prev_month(self) -> None:
        """Go to previous month."""
        year = self._current_date.year
        month = self._current_date.month - 1
        if month < 1:
            month = 12
            year -= 1
        self._current_date = date(year, month, 1)
        self._load_shows()
        self._render_view()

    def action_next_month(self) -> None:
        """Go to next month."""
        year = self._current_date.year
        month = self._current_date.month + 1
        if month > 12:
            month = 1
            year += 1
        self._current_date = date(year, month, 1)
        self._load_shows()
        self._render_view()

    def action_go_today(self) -> None:
        """Jump to current month."""
        self._current_date = date.today()
        self._load_shows()
        self._render_view()

    def action_new_show(self) -> None:
        """Open form to create new show."""
        from gigsly.screens.shows import ShowFormScreen
        self.app.push_screen(ShowFormScreen(), self._on_show_saved)

    def action_new_show_venue(self) -> None:
        """Open form to create new show with new venue."""
        from gigsly.screens.shows import ShowFormScreen
        self.app.push_screen(ShowFormScreen(create_venue=True), self._on_show_saved)

    def _on_show_saved(self, show_id: Optional[int]) -> None:
        """Handle show save callback."""
        if show_id:
            self.flash_success("Show added")
            self._load_shows()
            self._render_view()

    def action_view_day(self) -> None:
        """View day detail or show detail."""
        if self._view == "agenda":
            # View selected show
            try:
                table = self.query_one("#agenda-table", DataTable)
                if table.cursor_row is not None:
                    row_key = table.get_row_at(table.cursor_row)
                    if row_key:
                        key_value = str(table.get_row_key(row_key).value)
                        if key_value and not key_value.startswith("header-"):
                            from gigsly.screens.shows import ShowDetailScreen
                            self.app.push_screen(
                                ShowDetailScreen(int(key_value)),
                                self._on_detail_closed,
                            )
            except Exception:
                pass
        else:
            # In month view, show day detail modal
            self.app.push_screen(
                DayDetailScreen(self._current_date, self._shows),
                self._on_detail_closed,
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in agenda view."""
        if event.row_key:
            key_value = str(event.row_key.value)
            if key_value and not key_value.startswith("header-"):
                from gigsly.screens.shows import ShowDetailScreen
                self.app.push_screen(
                    ShowDetailScreen(int(key_value)),
                    self._on_detail_closed,
                )

    def _on_detail_closed(self, result) -> None:
        """Refresh when detail screen closes."""
        self._load_shows()
        self._render_view()

    def action_filter_menu(self) -> None:
        """Cycle through filter options (agenda view only)."""
        if self._view != "agenda":
            return

        filters = ["upcoming", "past", "all", "this_month"]
        current_idx = filters.index(self._filter) if self._filter in filters else 0
        next_idx = (current_idx + 1) % len(filters)
        self._filter = filters[next_idx]
        self._load_shows()
        self._render_view()

    def action_export_ics(self) -> None:
        """Export to ICS file."""
        from gigsly.ics_export import export_shows_to_ics

        with get_session() as session:
            shows = crud.get_upcoming_shows(session)
            if not shows:
                self.flash_warning("No upcoming shows to export")
                return

            try:
                # Export to default location
                from pathlib import Path
                output_path = Path.home() / ".gigsly" / "calendar.ics"
                export_shows_to_ics(shows, str(output_path))
                self.flash_success(f"Exported to {output_path}")
            except Exception as e:
                self.flash_error(f"Export failed: {e}")

    def action_go_to_venues(self) -> None:
        """Navigate to venues."""
        from gigsly.screens.venues import VenuesScreen
        self.app.switch_screen(VenuesScreen())

    def action_go_to_shows(self) -> None:
        """Navigate to shows."""
        from gigsly.screens.shows import ShowsScreen
        self.app.switch_screen(ShowsScreen())


class DayDetailScreen(ModalScreen):
    """Modal showing shows for a specific day."""

    CSS = """
    DayDetailScreen {
        align: center middle;
    }

    DayDetailScreen > Vertical {
        width: 50;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    DayDetailScreen .day-title {
        text-style: bold;
        margin-bottom: 1;
        text-align: center;
    }

    DayDetailScreen .show-list {
        margin: 1 0;
    }

    DayDetailScreen .button-bar {
        height: 3;
        align: right middle;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("n", "new_show", "New Show"),
        Binding("q", "close", "Close"),
    ]

    def __init__(self, current_date: date, shows: dict[date, list[Show]]) -> None:
        super().__init__()
        self._date = current_date
        self._shows = shows

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(
                self._date.strftime("%B %d, %Y"),
                classes="day-title",
            )

            shows = self._shows.get(self._date, [])
            if shows:
                content = "Shows:\n"
                for show in shows:
                    pay = f"${show.pay_amount:,.0f}" if show.pay_amount else "-"
                    content += f"  • {show.display_name} - {pay} ({show.payment_status})\n"
            else:
                content = "No shows on this day."

            yield Static(content, classes="show-list")

            with Horizontal(classes="button-bar"):
                yield Button("New Show", variant="primary", id="new-show")
                yield Button("Close", variant="default", id="close")

    def action_close(self) -> None:
        """Close the modal."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "close":
            self.dismiss(None)
        elif event.button.id == "new-show":
            self.action_new_show()

    def action_new_show(self) -> None:
        """Create a new show for this date."""
        from gigsly.screens.shows import ShowFormScreen
        self.app.push_screen(ShowFormScreen(), lambda r: self.dismiss(r))
