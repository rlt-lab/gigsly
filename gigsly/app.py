"""Textual TUI application for Gigsly."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Static


class GigslyApp(App):
    """Main Gigsly TUI application."""

    TITLE = "Gigsly"
    CSS = """
    Screen {
        align: center middle;
    }

    #welcome {
        width: 60;
        height: auto;
        padding: 2 4;
        border: solid green;
        text-align: center;
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

    def compose(self) -> ComposeResult:
        """Compose the initial UI."""
        yield Header()
        yield Static(
            "Welcome to Gigsly!\n\n"
            "Track your gigs, venues, payments, and booking outreach.\n\n"
            "Press [bold]v[/bold] for Venues, [bold]s[/bold] for Shows,\n"
            "[bold]c[/bold] for Calendar, or [bold]?[/bold] for help.",
            id="welcome",
        )
        yield Footer()

    def action_switch_screen(self, screen_name: str) -> None:
        """Switch to a different screen."""
        self.notify(f"{screen_name.title()} screen - Coming soon!")

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
