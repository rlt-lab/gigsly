"""Dropdown/select widget for Gigsly."""

from typing import Any, Generic, TypeVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, Input, Label, ListItem, ListView, Static

T = TypeVar("T")


class SelectOption(Generic[T]):
    """An option in a select widget."""

    def __init__(self, value: T, label: str = None) -> None:
        """Initialize the option.

        Args:
            value: The value for this option.
            label: Display label. Defaults to str(value).
        """
        self.value = value
        self.label = label if label is not None else str(value)

    def __str__(self) -> str:
        return self.label


class SelectWidget(Widget):
    """Dropdown select widget that opens a selection dialog."""

    DEFAULT_CSS = """
    SelectWidget {
        height: 3;
        width: 100%;
    }

    SelectWidget .select-button {
        width: 100%;
        height: 3;
    }

    SelectWidget .select-label {
        width: 1fr;
    }

    SelectWidget .select-arrow {
        width: 3;
        content-align: center middle;
    }
    """

    value: reactive[Any] = reactive(None)
    placeholder: reactive[str] = reactive("Select...")

    class Changed(Message):
        """Posted when the selection changes."""

        def __init__(self, value: Any) -> None:
            self.value = value
            super().__init__()

    def __init__(
        self,
        options: list[SelectOption | tuple[Any, str] | Any] = None,
        value: Any = None,
        placeholder: str = "Select...",
        allow_search: bool = True,
        **kwargs,
    ) -> None:
        """Initialize the select widget.

        Args:
            options: List of options. Can be SelectOption, (value, label) tuples, or values.
            value: Initial selected value.
            placeholder: Placeholder text when nothing selected.
            allow_search: If True, show search input in dropdown.
        """
        super().__init__(**kwargs)
        self._options = self._normalize_options(options or [])
        self.value = value
        self.placeholder = placeholder
        self.allow_search = allow_search

    def _normalize_options(self, options: list) -> list[SelectOption]:
        """Normalize options to SelectOption list."""
        result = []
        for opt in options:
            if isinstance(opt, SelectOption):
                result.append(opt)
            elif isinstance(opt, tuple) and len(opt) == 2:
                result.append(SelectOption(opt[0], opt[1]))
            else:
                result.append(SelectOption(opt))
        return result

    @property
    def options(self) -> list[SelectOption]:
        """Get the list of options."""
        return self._options

    @options.setter
    def options(self, value: list) -> None:
        """Set the list of options."""
        self._options = self._normalize_options(value)
        self._update_display()

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Button(self._display_text(), id="select-trigger", classes="select-button")

    def _display_text(self) -> str:
        """Get the display text for the current value."""
        if self.value is None:
            return self.placeholder

        for opt in self._options:
            if opt.value == self.value:
                return opt.label

        return str(self.value)

    def _update_display(self) -> None:
        """Update the displayed text."""
        try:
            button = self.query_one("#select-trigger", Button)
            button.label = self._display_text()
        except Exception:
            pass

    def watch_value(self, old_value: Any, new_value: Any) -> None:
        """React to value changes."""
        self._update_display()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press to open dropdown."""
        if event.button.id == "select-trigger":
            dialog = SelectDialog(
                options=self._options,
                value=self.value,
                allow_search=self.allow_search,
            )
            result = await self.app.push_screen_wait(dialog)
            if result is not None:
                self.value = result
                self.post_message(self.Changed(result))


class SelectDialog(ModalScreen):
    """Modal select dialog with optional search."""

    DEFAULT_CSS = """
    SelectDialog {
        align: center middle;
    }

    SelectDialog > Vertical {
        width: 50;
        max-height: 80%;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    SelectDialog .search-input {
        margin-bottom: 1;
    }

    SelectDialog ListView {
        height: auto;
        max-height: 20;
        border: solid $primary-lighten-3;
    }

    SelectDialog ListItem {
        padding: 0 1;
    }

    SelectDialog ListItem.selected {
        background: $primary;
    }

    SelectDialog .button-bar {
        height: 3;
        width: 100%;
        align: right middle;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select", show=False),
    ]

    def __init__(
        self,
        options: list[SelectOption],
        value: Any = None,
        allow_search: bool = True,
        **kwargs,
    ) -> None:
        """Initialize the select dialog."""
        super().__init__(**kwargs)
        self._options = options
        self._value = value
        self._allow_search = allow_search
        self._filtered_options = options.copy()

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Vertical():
            if self._allow_search:
                yield Input(placeholder="Search...", id="search", classes="search-input")

            yield ListView(id="options-list")

            with Vertical(classes="button-bar"):
                yield Button("Cancel", variant="default", id="cancel")

    def on_mount(self) -> None:
        """Populate the list on mount."""
        self._populate_list()
        if self._allow_search:
            self.query_one("#search", Input).focus()
        else:
            self.query_one("#options-list", ListView).focus()

    def _populate_list(self, filter_text: str = "") -> None:
        """Populate the options list."""
        list_view = self.query_one("#options-list", ListView)
        list_view.clear()

        filter_lower = filter_text.lower()
        self._filtered_options = [
            opt for opt in self._options if filter_lower in opt.label.lower()
        ]

        for i, opt in enumerate(self._filtered_options):
            item = ListItem(Label(opt.label), id=f"option-{i}")
            if opt.value == self._value:
                item.add_class("selected")
            list_view.append(item)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search":
            self._populate_list(event.value)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle option selection."""
        if event.item and event.item.id:
            idx = int(event.item.id.split("-")[1])
            if 0 <= idx < len(self._filtered_options):
                self.dismiss(self._filtered_options[idx].value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel":
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Cancel and dismiss."""
        self.dismiss(None)

    def action_select(self) -> None:
        """Select the highlighted option."""
        list_view = self.query_one("#options-list", ListView)
        if list_view.highlighted_child:
            idx = list_view.index
            if 0 <= idx < len(self._filtered_options):
                self.dismiss(self._filtered_options[idx].value)


async def select_option(
    app,
    options: list[SelectOption | tuple[Any, str] | Any],
    value: Any = None,
    allow_search: bool = True,
) -> Any | None:
    """Show a select dialog and wait for the result.

    Args:
        app: The Textual app instance.
        options: List of options.
        value: Initial selected value.
        allow_search: If True, show search input.

    Returns:
        Selected value or None if cancelled.
    """
    # Normalize options
    normalized = []
    for opt in options:
        if isinstance(opt, SelectOption):
            normalized.append(opt)
        elif isinstance(opt, tuple) and len(opt) == 2:
            normalized.append(SelectOption(opt[0], opt[1]))
        else:
            normalized.append(SelectOption(opt))

    dialog = SelectDialog(options=normalized, value=value, allow_search=allow_search)
    return await app.push_screen_wait(dialog)
