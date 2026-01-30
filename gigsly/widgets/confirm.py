"""Confirmation dialog widget for Gigsly."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class ConfirmDialog(ModalScreen[bool]):
    """Modal confirmation dialog.

    Optionally requires typing a confirmation word (e.g., "DELETE").
    """

    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }

    ConfirmDialog > Vertical {
        width: 60;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
    }

    ConfirmDialog .title {
        text-style: bold;
        margin-bottom: 1;
    }

    ConfirmDialog .message {
        margin-bottom: 1;
    }

    ConfirmDialog .confirm-input-container {
        height: auto;
        margin-bottom: 1;
    }

    ConfirmDialog .confirm-hint {
        color: $warning;
        margin-bottom: 1;
    }

    ConfirmDialog .button-bar {
        height: 3;
        align: right middle;
    }

    ConfirmDialog Button {
        margin-left: 1;
    }

    ConfirmDialog .danger {
        background: $error;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "submit", "Confirm", show=False),
    ]

    def __init__(
        self,
        title: str = "Confirm",
        message: str = "Are you sure?",
        confirm_word: str = None,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
        danger: bool = False,
        **kwargs,
    ) -> None:
        """Initialize the confirmation dialog.

        Args:
            title: Dialog title.
            message: Message to display.
            confirm_word: If set, user must type this word to confirm.
            confirm_label: Label for the confirm button.
            cancel_label: Label for the cancel button.
            danger: If True, style confirm button as dangerous action.
        """
        super().__init__(**kwargs)
        self.dialog_title = title
        self.dialog_message = message
        self.confirm_word = confirm_word
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label
        self.danger = danger

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Vertical():
            yield Label(self.dialog_title, classes="title")
            yield Static(self.dialog_message, classes="message")

            if self.confirm_word:
                with Vertical(classes="confirm-input-container"):
                    yield Label(
                        f'Type "{self.confirm_word}" to confirm:',
                        classes="confirm-hint",
                    )
                    yield Input(placeholder=self.confirm_word, id="confirm-input")

            with Horizontal(classes="button-bar"):
                yield Button(self.cancel_label, variant="default", id="cancel")
                button_classes = "danger" if self.danger else ""
                yield Button(
                    self.confirm_label,
                    variant="primary" if not self.danger else "error",
                    id="confirm",
                    classes=button_classes,
                )

    def on_mount(self) -> None:
        """Focus the input if present, otherwise the cancel button."""
        if self.confirm_word:
            self.query_one("#confirm-input", Input).focus()
        else:
            self.query_one("#cancel", Button).focus()

    def action_cancel(self) -> None:
        """Cancel and dismiss."""
        self.dismiss(False)

    def action_submit(self) -> None:
        """Submit if valid."""
        self._try_confirm()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel":
            self.dismiss(False)
        elif event.button.id == "confirm":
            self._try_confirm()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        self._try_confirm()

    def _try_confirm(self) -> None:
        """Try to confirm, checking the confirm word if required."""
        if self.confirm_word:
            input_widget = self.query_one("#confirm-input", Input)
            if input_widget.value.upper() != self.confirm_word.upper():
                input_widget.add_class("error")
                self.app.bell()
                return
        self.dismiss(True)


async def confirm(
    app,
    title: str = "Confirm",
    message: str = "Are you sure?",
    confirm_word: str = None,
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
    danger: bool = False,
) -> bool:
    """Show a confirmation dialog and wait for the result.

    Args:
        app: The Textual app instance.
        title: Dialog title.
        message: Message to display.
        confirm_word: If set, user must type this word to confirm.
        confirm_label: Label for the confirm button.
        cancel_label: Label for the cancel button.
        danger: If True, style confirm button as dangerous action.

    Returns:
        True if confirmed, False if cancelled.
    """
    dialog = ConfirmDialog(
        title=title,
        message=message,
        confirm_word=confirm_word,
        confirm_label=confirm_label,
        cancel_label=cancel_label,
        danger=danger,
    )
    return await app.push_screen_wait(dialog)


async def confirm_delete(app, item_name: str) -> bool:
    """Show a delete confirmation dialog requiring "DELETE" to be typed.

    Args:
        app: The Textual app instance.
        item_name: Name of the item being deleted.

    Returns:
        True if deletion confirmed, False otherwise.
    """
    return await confirm(
        app,
        title="Confirm Delete",
        message=f"This will permanently delete {item_name}.\n"
        "This action cannot be undone.",
        confirm_word="DELETE",
        confirm_label="Delete",
        danger=True,
    )
