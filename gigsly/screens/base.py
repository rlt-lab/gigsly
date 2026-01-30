"""Base screen class for Gigsly TUI."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header

from gigsly.widgets.flash import FlashMessage


class BaseScreen(Screen):
    """Base screen with common functionality for all Gigsly screens."""

    BINDINGS = [
        Binding("q", "go_back", "Back"),
        Binding("?", "show_help", "Help"),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._flash = None

    def compose_header(self) -> ComposeResult:
        """Compose the header. Override for custom headers."""
        yield Header()

    def compose_footer(self) -> ComposeResult:
        """Compose the footer."""
        yield Footer()

    def compose_flash(self) -> ComposeResult:
        """Compose the flash message widget."""
        yield FlashMessage()

    def action_go_back(self) -> None:
        """Go back to previous screen or quit."""
        if len(self.app.screen_stack) > 1:
            self.app.pop_screen()
        else:
            self.app.exit()

    def action_show_help(self) -> None:
        """Show help overlay."""
        self.app.notify("Help overlay - Coming soon!")

    def flash_success(self, message: str, duration: float = 3.0) -> None:
        """Show a success flash message."""
        try:
            flash = self.query_one(FlashMessage)
            flash.auto_dismiss = duration
            flash.show(message, "success")
        except Exception:
            self.app.notify(message, severity="information")

    def flash_warning(self, message: str, duration: float = 5.0) -> None:
        """Show a warning flash message."""
        try:
            flash = self.query_one(FlashMessage)
            flash.auto_dismiss = duration
            flash.show(message, "warning")
        except Exception:
            self.app.notify(message, severity="warning")

    def flash_error(self, message: str, duration: float = 0) -> None:
        """Show an error flash message."""
        try:
            flash = self.query_one(FlashMessage)
            flash.auto_dismiss = duration
            flash.show(message, "error")
        except Exception:
            self.app.notify(message, severity="error")
