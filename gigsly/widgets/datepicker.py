"""Date picker widget for Gigsly."""

import calendar
from datetime import date, timedelta

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, Label, Static


class DatePicker(Widget):
    """Inline date picker widget.

    Displays a calendar month view with navigation.
    """

    DEFAULT_CSS = """
    DatePicker {
        width: auto;
        height: auto;
        padding: 1;
        background: $surface;
        border: solid $primary;
    }

    DatePicker .header {
        width: 100%;
        height: 1;
        margin-bottom: 1;
    }

    DatePicker .month-label {
        width: 1fr;
        content-align: center middle;
        text-style: bold;
    }

    DatePicker .nav-button {
        width: 3;
        min-width: 3;
    }

    DatePicker .weekday-header {
        width: 100%;
        height: 1;
        margin-bottom: 1;
    }

    DatePicker .weekday {
        width: 4;
        content-align: center middle;
        color: $text-muted;
    }

    DatePicker .calendar-grid {
        width: 28;
        height: auto;
        grid-size: 7;
        grid-gutter: 0;
    }

    DatePicker .day {
        width: 4;
        height: 1;
        content-align: center middle;
    }

    DatePicker .day.other-month {
        color: $text-disabled;
    }

    DatePicker .day.today {
        text-style: bold underline;
    }

    DatePicker .day.selected {
        background: $primary;
        color: $text;
    }

    DatePicker .day:hover {
        background: $primary-lighten-2;
    }
    """

    BINDINGS = [
        Binding("left", "prev_day", "Previous day", show=False),
        Binding("right", "next_day", "Next day", show=False),
        Binding("up", "prev_week", "Previous week", show=False),
        Binding("down", "next_week", "Next week", show=False),
        Binding("h", "prev_month", "Previous month"),
        Binding("l", "next_month", "Next month"),
        Binding("t", "today", "Today"),
        Binding("enter", "select", "Select", show=False),
    ]

    selected_date: reactive[date] = reactive(date.today)
    view_month: reactive[date] = reactive(date.today)

    class DateSelected(Message):
        """Posted when a date is selected."""

        def __init__(self, date_value: date) -> None:
            self.date = date_value
            super().__init__()

    def __init__(self, initial_date: date = None, **kwargs) -> None:
        """Initialize the date picker.

        Args:
            initial_date: Initial selected date. Defaults to today.
        """
        super().__init__(**kwargs)
        self.selected_date = initial_date or date.today()
        self.view_month = date(self.selected_date.year, self.selected_date.month, 1)

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        # Header with navigation
        with Horizontal(classes="header"):
            yield Button("<", id="prev-month", classes="nav-button")
            yield Label(self._month_label(), id="month-label", classes="month-label")
            yield Button(">", id="next-month", classes="nav-button")

        # Weekday headers
        with Horizontal(classes="weekday-header"):
            for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
                yield Static(day, classes="weekday")

        # Calendar grid
        with Grid(classes="calendar-grid"):
            for day_info in self._get_calendar_days():
                yield self._create_day_cell(day_info)

    def _month_label(self) -> str:
        """Get the month/year label."""
        return self.view_month.strftime("%B %Y")

    def _get_calendar_days(self) -> list[dict]:
        """Get calendar days for the current view month."""
        year, month = self.view_month.year, self.view_month.month
        cal = calendar.Calendar(firstweekday=0)  # Monday first

        days = []
        for d in cal.itermonthdates(year, month):
            days.append(
                {
                    "date": d,
                    "is_current_month": d.month == month,
                    "is_today": d == date.today(),
                    "is_selected": d == self.selected_date,
                }
            )
        return days

    def _create_day_cell(self, day_info: dict) -> Static:
        """Create a day cell widget."""
        d = day_info["date"]
        classes = ["day"]

        if not day_info["is_current_month"]:
            classes.append("other-month")
        if day_info["is_today"]:
            classes.append("today")
        if day_info["is_selected"]:
            classes.append("selected")

        return Static(str(d.day), classes=" ".join(classes), id=f"day-{d.isoformat()}")

    def _refresh_calendar(self) -> None:
        """Refresh the calendar display."""
        # Update month label
        month_label = self.query_one("#month-label", Label)
        month_label.update(self._month_label())

        # Update day cells
        grid = self.query_one(".calendar-grid", Grid)
        grid.remove_children()
        for day_info in self._get_calendar_days():
            grid.mount(self._create_day_cell(day_info))

    def watch_view_month(self, old_value: date, new_value: date) -> None:
        """React to view month changes."""
        if old_value != new_value:
            self._refresh_calendar()

    def watch_selected_date(self, old_value: date, new_value: date) -> None:
        """React to selected date changes."""
        if old_value != new_value:
            self._refresh_calendar()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle navigation button presses."""
        if event.button.id == "prev-month":
            self.action_prev_month()
        elif event.button.id == "next-month":
            self.action_next_month()

    def on_static_click(self, event: Static.Click) -> None:
        """Handle day cell clicks."""
        if event.static.id and event.static.id.startswith("day-"):
            date_str = event.static.id[4:]
            try:
                self.selected_date = date.fromisoformat(date_str)
                self.post_message(self.DateSelected(self.selected_date))
            except ValueError:
                pass

    def action_prev_month(self) -> None:
        """Navigate to previous month."""
        year, month = self.view_month.year, self.view_month.month
        if month == 1:
            self.view_month = date(year - 1, 12, 1)
        else:
            self.view_month = date(year, month - 1, 1)

    def action_next_month(self) -> None:
        """Navigate to next month."""
        year, month = self.view_month.year, self.view_month.month
        if month == 12:
            self.view_month = date(year + 1, 1, 1)
        else:
            self.view_month = date(year, month + 1, 1)

    def action_prev_day(self) -> None:
        """Select previous day."""
        self.selected_date = self.selected_date - timedelta(days=1)
        self._ensure_date_visible()

    def action_next_day(self) -> None:
        """Select next day."""
        self.selected_date = self.selected_date + timedelta(days=1)
        self._ensure_date_visible()

    def action_prev_week(self) -> None:
        """Select previous week."""
        self.selected_date = self.selected_date - timedelta(weeks=1)
        self._ensure_date_visible()

    def action_next_week(self) -> None:
        """Select next week."""
        self.selected_date = self.selected_date + timedelta(weeks=1)
        self._ensure_date_visible()

    def action_today(self) -> None:
        """Jump to today."""
        self.selected_date = date.today()
        self._ensure_date_visible()

    def action_select(self) -> None:
        """Emit the selected date."""
        self.post_message(self.DateSelected(self.selected_date))

    def _ensure_date_visible(self) -> None:
        """Ensure the selected date is in the view month."""
        if (
            self.selected_date.year != self.view_month.year
            or self.selected_date.month != self.view_month.month
        ):
            self.view_month = date(self.selected_date.year, self.selected_date.month, 1)


class DatePickerDialog(ModalScreen[date | None]):
    """Modal date picker dialog."""

    DEFAULT_CSS = """
    DatePickerDialog {
        align: center middle;
    }

    DatePickerDialog > Vertical {
        width: auto;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    DatePickerDialog .button-bar {
        height: 3;
        width: 100%;
        align: right middle;
        margin-top: 1;
    }

    DatePickerDialog Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, initial_date: date = None, title: str = "Select Date", **kwargs) -> None:
        """Initialize the date picker dialog.

        Args:
            initial_date: Initial selected date. Defaults to today.
            title: Dialog title.
        """
        super().__init__(**kwargs)
        self.initial_date = initial_date or date.today()
        self.dialog_title = title

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Vertical():
            yield Label(self.dialog_title, classes="title")
            yield DatePicker(initial_date=self.initial_date, id="picker")
            with Horizontal(classes="button-bar"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Select", variant="primary", id="select")

    def on_date_picker_date_selected(self, event: DatePicker.DateSelected) -> None:
        """Handle date selection."""
        self.dismiss(event.date)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "select":
            picker = self.query_one("#picker", DatePicker)
            self.dismiss(picker.selected_date)

    def action_cancel(self) -> None:
        """Cancel and dismiss."""
        self.dismiss(None)


async def pick_date(app, initial_date: date = None, title: str = "Select Date") -> date | None:
    """Show a date picker dialog and wait for the result.

    Args:
        app: The Textual app instance.
        initial_date: Initial selected date.
        title: Dialog title.

    Returns:
        Selected date or None if cancelled.
    """
    dialog = DatePickerDialog(initial_date=initial_date, title=title)
    return await app.push_screen_wait(dialog)
