"""Flash message widget for Gigsly."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static


class FlashMessage(Widget):
    """Flash message widget with auto-dismiss.

    Displays success, warning, or error messages that automatically
    disappear after a configurable duration.
    """

    DEFAULT_CSS = """
    FlashMessage {
        dock: top;
        height: auto;
        width: 100%;
        display: none;
    }

    FlashMessage.visible {
        display: block;
    }

    FlashMessage .flash-content {
        padding: 1 2;
        margin: 0 1;
    }

    FlashMessage.success .flash-content {
        background: $success-darken-2;
        color: $text;
        border: solid $success;
    }

    FlashMessage.warning .flash-content {
        background: $warning-darken-2;
        color: $text;
        border: solid $warning;
    }

    FlashMessage.error .flash-content {
        background: $error-darken-2;
        color: $text;
        border: solid $error;
    }

    FlashMessage .flash-dismiss {
        dock: right;
        width: 3;
        content-align: center middle;
    }
    """

    message: reactive[str] = reactive("")
    level: reactive[str] = reactive("success")

    class Dismissed(Message):
        """Posted when the flash message is dismissed."""

        pass

    def __init__(
        self,
        message: str = "",
        level: str = "success",
        auto_dismiss: float = 3.0,
        **kwargs,
    ) -> None:
        """Initialize the flash message.

        Args:
            message: The message to display.
            level: Message level - "success", "warning", or "error".
            auto_dismiss: Seconds before auto-dismiss. 0 to disable.
        """
        super().__init__(**kwargs)
        self.message = message
        self.level = level
        self.auto_dismiss = auto_dismiss
        self._dismiss_timer = None

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        with Horizontal(classes="flash-content"):
            yield Static(self.message, id="flash-text")
            yield Static("×", classes="flash-dismiss")

    def on_mount(self) -> None:
        """Handle mount event."""
        self._update_classes()
        if self.message:
            self.show()

    def watch_message(self, message: str) -> None:
        """React to message changes."""
        text_widget = self.query_one("#flash-text", Static)
        text_widget.update(message)

    def watch_level(self, level: str) -> None:
        """React to level changes."""
        self._update_classes()

    def _update_classes(self) -> None:
        """Update CSS classes based on current level."""
        self.remove_class("success", "warning", "error")
        if self.level in ("success", "warning", "error"):
            self.add_class(self.level)

    def show(self, message: str = None, level: str = None) -> None:
        """Show the flash message.

        Args:
            message: Optional new message to display.
            level: Optional new level.
        """
        if message is not None:
            self.message = message
        if level is not None:
            self.level = level
            self._update_classes()

        self.add_class("visible")

        # Cancel existing timer
        if self._dismiss_timer:
            self._dismiss_timer.stop()
            self._dismiss_timer = None

        # Start auto-dismiss timer
        if self.auto_dismiss > 0:
            self._dismiss_timer = self.set_timer(
                self.auto_dismiss, self.dismiss, name="flash_dismiss"
            )

    def dismiss(self) -> None:
        """Dismiss the flash message."""
        self.remove_class("visible")
        if self._dismiss_timer:
            self._dismiss_timer.stop()
            self._dismiss_timer = None
        self.post_message(self.Dismissed())

    def on_click(self, event) -> None:
        """Handle click to dismiss."""
        self.dismiss()


def flash_success(app, message: str, duration: float = 3.0) -> None:
    """Show a success flash message.

    Args:
        app: The Textual app instance.
        message: Message to display.
        duration: Auto-dismiss duration in seconds.
    """
    try:
        flash = app.query_one(FlashMessage)
        flash.auto_dismiss = duration
        flash.show(message, "success")
    except Exception:
        app.notify(message, severity="information")


def flash_warning(app, message: str, duration: float = 5.0) -> None:
    """Show a warning flash message."""
    try:
        flash = app.query_one(FlashMessage)
        flash.auto_dismiss = duration
        flash.show(message, "warning")
    except Exception:
        app.notify(message, severity="warning")


def flash_error(app, message: str, duration: float = 0) -> None:
    """Show an error flash message.

    Errors don't auto-dismiss by default.
    """
    try:
        flash = app.query_one(FlashMessage)
        flash.auto_dismiss = duration
        flash.show(message, "error")
    except Exception:
        app.notify(message, severity="error")
