"""Dashboard screen for Gigsly TUI."""

from datetime import date, timedelta
from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.timer import Timer
from textual.widgets import (
    Button,
    Footer,
    Header,
    ListItem,
    ListView,
    Static,
)

from gigsly.db.models import Show, Venue
from gigsly.db.session import get_session
from gigsly.db import crud
from gigsly.screens.base import BaseScreen
from gigsly.widgets.flash import FlashMessage


class DashboardScreen(BaseScreen):
    """Main dashboard screen."""

    TITLE = "Dashboard"

    CSS = """
    DashboardScreen {
        layout: vertical;
    }

    .stats-row {
        height: 7;
        padding: 1 2;
    }

    .stat-box {
        width: 1fr;
        height: 5;
        border: thick $primary;
        content-align: center middle;
        margin: 0 1;
        padding: 0 1;
    }

    .stat-box .stat-value {
        text-style: bold;
        text-align: center;
    }

    .stat-box .stat-label {
        text-align: center;
        color: $text-muted;
    }

    .stat-box.unpaid-warning {
        border: thick $warning;
    }

    .section-title {
        text-style: bold;
        padding: 0 2;
        margin-top: 1;
    }

    .section-content {
        padding: 0 2 1 2;
        height: auto;
    }

    .upcoming-list {
        height: auto;
        padding: 0 2;
    }

    .attention-list {
        height: auto;
        padding: 0 2;
    }

    .attention-item {
        height: 3;
        padding: 0 1;
        border: solid $primary-lighten-3;
        margin-bottom: 1;
    }

    .attention-item.priority-high {
        border: solid $error;
    }

    .attention-item.priority-medium {
        border: solid $warning;
    }

    .nav-bar {
        dock: bottom;
        height: 3;
        padding: 0 2;
    }

    .empty-state {
        padding: 2;
        text-align: center;
    }

    .getting-started {
        padding: 2;
        margin: 1 2;
        border: solid $primary;
    }
    """

    BINDINGS = [
        Binding("v", "go_to_venues", "Venues"),
        Binding("s", "go_to_shows", "Shows"),
        Binding("c", "go_to_calendar", "Calendar"),
        Binding("r", "go_to_report", "Report"),
        Binding("n", "new_show", "New Show"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("enter", "activate_item", "View", show=False),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._refresh_timer: Optional[Timer] = None
        self._attention_items: list[dict] = []
        self._upcoming_shows: list[Show] = []
        self._is_new_user = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield from self.compose_flash()

        with VerticalScroll():
            with Horizontal(classes="stats-row"):
                with Vertical(classes="stat-box", id="stat-upcoming"):
                    yield Static("-", classes="stat-value", id="upcoming-value")
                    yield Static("UPCOMING", classes="stat-label")

                with Vertical(classes="stat-box", id="stat-ytd"):
                    yield Static("-", classes="stat-value", id="ytd-value")
                    yield Static("YTD EARNED", classes="stat-label")

                with Vertical(classes="stat-box", id="stat-unpaid"):
                    yield Static("-", classes="stat-value", id="unpaid-value")
                    yield Static("UNPAID", classes="stat-label")

            yield Static("", id="main-content")

        yield Footer()

    def on_mount(self) -> None:
        """Load dashboard data."""
        self._load_data()
        # Set up auto-refresh every 60 seconds
        self._refresh_timer = self.set_interval(60, self._load_data)
        # Show welcome modal if first run
        if self._is_new_user:
            self.call_later(self._show_welcome)

    def on_unmount(self) -> None:
        """Clean up timer."""
        if self._refresh_timer:
            self._refresh_timer.stop()

    def _show_welcome(self) -> None:
        """Show welcome modal for first-time users."""
        from gigsly.screens.onboarding import WelcomeModal
        self.app.push_screen(WelcomeModal())

    def _load_data(self) -> None:
        """Load all dashboard data."""
        today = date.today()
        year_start = date(today.year, 1, 1)

        with get_session() as session:
            # Get upcoming shows
            upcoming_shows = crud.get_upcoming_shows(session)
            self._upcoming_shows = upcoming_shows[:5]  # Keep first 5 for display

            # Calculate stats
            upcoming_count = len(upcoming_shows)

            # YTD earnings
            all_shows = crud.get_shows_in_range(session, year_start, today)
            ytd_earned = sum(
                s.pay_amount or 0
                for s in all_shows
                if s.payment_status == "paid"
            )

            # Unpaid balance
            unpaid_shows = crud.get_unpaid_shows(session)
            unpaid_total = sum(s.pay_amount or 0 for s in unpaid_shows)
            unpaid_count = len(unpaid_shows)

            # Check if new user (no venues)
            venues = crud.get_all_venues(session)
            self._is_new_user = len(venues) == 0

            # Build attention items
            self._attention_items = self._build_attention_items(session, today)

        # Update display
        self._update_stats(upcoming_count, ytd_earned, unpaid_total, unpaid_count)
        self._update_content()

    def _update_stats(
        self, upcoming: int, ytd: float, unpaid: float, unpaid_count: int
    ) -> None:
        """Update the stats cards."""
        self.query_one("#upcoming-value", Static).update(str(upcoming))
        self.query_one("#ytd-value", Static).update(f"${ytd:,.0f}")

        unpaid_text = f"${unpaid:,.0f}"
        if unpaid_count > 0:
            unpaid_text += f"\n({unpaid_count} shows)"
        self.query_one("#unpaid-value", Static).update(unpaid_text)

        # Highlight unpaid if > 0
        unpaid_box = self.query_one("#stat-unpaid", Vertical)
        if unpaid > 0:
            unpaid_box.add_class("unpaid-warning")
        else:
            unpaid_box.remove_class("unpaid-warning")

    def _update_content(self) -> None:
        """Update the main content area."""
        if self._is_new_user:
            content = self._build_getting_started()
        else:
            content = self._build_normal_content()

        self.query_one("#main-content", Static).update(content)

    def _build_getting_started(self) -> str:
        """Build getting started content for new users."""
        return """
[bold]─── GETTING STARTED ─────────────────────────────────[/bold]

Welcome to Gigsly! Here's how to get started:

  1. Press [bold]v[/bold] to add your first venue
  2. Press [bold]n[/bold] to add a show
  3. Press [bold]r[/bold] to see your action report

Track your gigs, payments, and booking outreach all in one place.
"""

    def _build_normal_content(self) -> str:
        """Build normal dashboard content."""
        today = date.today()
        two_weeks = today + timedelta(days=14)

        # Next 14 days section
        content = "\n[bold]─── NEXT 14 DAYS ───────────────────────────────────────[/bold]\n\n"

        upcoming_in_range = [s for s in self._upcoming_shows if s.date <= two_weeks]

        if not upcoming_in_range:
            content += "  No shows in the next 2 weeks\n"
        else:
            for show in upcoming_in_range[:5]:
                day = show.date.strftime("%a %b %d")
                pay = f"${show.pay_amount:,.0f}" if show.pay_amount else "-"
                content += f"  {day}   {show.display_name:<20} {pay:>8}   {show.payment_status}\n"

            total = len([s for s in self._upcoming_shows if s.date <= two_weeks])
            if total > 5:
                content += f"\n  ... and {total - 5} more\n"

        # Needs attention section
        content += "\n[bold]─── NEEDS ATTENTION ────────────────────────────────────[/bold]\n\n"

        if not self._attention_items:
            content += "  [green]✓ All caught up![/green]\n"
        else:
            for item in self._attention_items[:5]:
                icon = item.get("icon", "⚠")
                text = item["text"]
                if item.get("priority") == "high":
                    content += f"  [red]{icon} {text}[/red]\n"
                elif item.get("priority") == "medium":
                    content += f"  [yellow]{icon} {text}[/yellow]\n"
                else:
                    content += f"  {icon} {text}\n"

        return content

    def _build_attention_items(self, session, today: date) -> list[dict]:
        """Build the attention items list with priority ordering."""
        items = []

        # 1. Overdue payments (highest priority)
        overdue = [
            s for s in crud.get_unpaid_shows(session)
            if (today - s.date).days >= 30
        ]
        if overdue:
            items.append({
                "text": f"{len(overdue)} payment{'s' if len(overdue) > 1 else ''} overdue",
                "icon": "⚠",
                "priority": "high",
                "action": "shows_unpaid",
            })

        # 2. Invoices needing sending
        needs_invoice = crud.get_shows_needing_invoice(session)
        if needs_invoice:
            items.append({
                "text": f"{len(needs_invoice)} invoice{'s' if len(needs_invoice) > 1 else ''} need{'s' if len(needs_invoice) == 1 else ''} sending",
                "icon": "⚠",
                "priority": "medium",
                "action": "shows_invoice",
            })

        # 3. Booking windows opening soon
        venues = crud.get_all_venues(session)
        for venue in venues:
            if venue.booking_window_start:
                # Check if booking window opens within 7 days
                current_day = today.day
                window_start = venue.booking_window_start
                days_until = window_start - current_day
                if days_until < 0:
                    days_until += 30  # Approximate for next month

                if 0 < days_until <= 7:
                    items.append({
                        "text": f"Booking window opens in {days_until} day{'s' if days_until != 1 else ''} ({venue.name})",
                        "icon": "📅",
                        "priority": "medium",
                        "action": f"venue_{venue.id}",
                    })

        # 4. Venues with no upcoming shows
        for venue in venues:
            upcoming = [
                s for s in venue.shows
                if s.date >= today and not s.is_cancelled
            ]
            if not upcoming and venue.shows:  # Has past shows but no upcoming
                items.append({
                    "text": f"No upcoming shows at {venue.name}",
                    "icon": "📍",
                    "priority": "low",
                    "action": f"venue_{venue.id}",
                })

        # 5. Contact reminders (60+ days since last contact)
        for venue in venues:
            if venue.contact_logs:
                latest = max(venue.contact_logs, key=lambda c: c.contacted_at)
                days_since = (today - latest.contacted_at.date()).days
                if days_since >= 60:
                    items.append({
                        "text": f"Haven't contacted {venue.name} in {days_since} days",
                        "icon": "📞",
                        "priority": "low",
                        "action": f"venue_{venue.id}",
                    })

        return items

    def action_refresh(self) -> None:
        """Manually refresh dashboard data."""
        self._load_data()
        self.flash_success("Dashboard refreshed")

    def action_go_to_venues(self) -> None:
        """Navigate to venues screen."""
        from gigsly.screens.venues import VenuesScreen
        self.app.switch_screen(VenuesScreen())

    def action_go_to_shows(self) -> None:
        """Navigate to shows screen."""
        from gigsly.screens.shows import ShowsScreen
        self.app.switch_screen(ShowsScreen())

    def action_go_to_calendar(self) -> None:
        """Navigate to calendar screen."""
        from gigsly.screens.calendar import CalendarScreen
        self.app.switch_screen(CalendarScreen())

    def action_go_to_report(self) -> None:
        """Navigate to report screen."""
        self.app.notify("Full Report - Coming soon!")

    def action_new_show(self) -> None:
        """Add a new show."""
        from gigsly.screens.shows import ShowFormScreen
        self.app.push_screen(ShowFormScreen(), self._on_show_saved)

    def _on_show_saved(self, show_id: Optional[int]) -> None:
        """Handle show save callback."""
        if show_id:
            self.flash_success("Show added")
            self._load_data()

    def action_activate_item(self) -> None:
        """Activate the currently selected attention item."""
        # For now, just go to the relevant screen
        if self._attention_items:
            item = self._attention_items[0]
            action = item.get("action", "")
            if action.startswith("venue_"):
                venue_id = int(action.split("_")[1])
                from gigsly.screens.venues import VenueDetailScreen
                self.app.push_screen(VenueDetailScreen(venue_id))
            elif action in ("shows_unpaid", "shows_invoice"):
                from gigsly.screens.shows import ShowsScreen
                self.app.push_screen(ShowsScreen())

    def action_cursor_up(self) -> None:
        """Move cursor up in attention list."""
        pass  # Will be implemented with proper ListView

    def action_cursor_down(self) -> None:
        """Move cursor down in attention list."""
        pass  # Will be implemented with proper ListView

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
