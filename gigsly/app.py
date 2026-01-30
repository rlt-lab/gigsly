"""Textual TUI application for Gigsly."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Static

from gigsly.db.session import init_db
from gigsly.screens.dashboard import DashboardScreen
from gigsly.screens.venues import VenuesScreen
from gigsly.screens.shows import ShowsScreen
from gigsly.screens.calendar import CalendarScreen


class GigslyApp(App):
    """Main Gigsly TUI application."""

    TITLE = "Gigsly"

    CSS = """
    Screen {
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("d", "switch_screen('dashboard')", "Dashboard"),
        Binding("v", "switch_screen('venues')", "Venues"),
        Binding("s", "switch_screen('shows')", "Shows"),
        Binding("c", "switch_screen('calendar')", "Calendar"),
        Binding("r", "switch_screen('report')", "Report"),
        Binding("?", "show_help", "Help"),
        Binding("ctrl+comma", "settings", "Settings"),
        Binding("q", "quit", "Quit"),
    ]

    SCREENS = {
        "dashboard": DashboardScreen,
        "venues": VenuesScreen,
        "shows": ShowsScreen,
        "calendar": CalendarScreen,
    }

    def on_mount(self) -> None:
        """Initialize the app and show dashboard."""
        # Ensure database is initialized
        init_db()
        # Push the dashboard screen
        self.push_screen(DashboardScreen())

    def action_switch_screen(self, screen_name: str) -> None:
        """Switch to a different screen."""
        if screen_name == "report":
            self.notify("Full Report - Coming soon!")
            return

        screen_class = self.SCREENS.get(screen_name)
        if screen_class:
            self.switch_screen(screen_class())
        else:
            self.notify(f"Unknown screen: {screen_name}")

    def action_show_help(self) -> None:
        """Show help overlay."""
        self.notify("Help overlay - Coming soon!")

    def action_settings(self) -> None:
        """Show settings screen."""
        self.notify("Settings screen - Coming soon!")


def run_app() -> None:
    """Run the Gigsly TUI application."""
    app = GigslyApp()
    app.run()


if __name__ == "__main__":
    run_app()
