"""Onboarding screens for Gigsly TUI."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class WelcomeModal(ModalScreen[bool]):
    """Welcome modal for first-time users."""

    CSS = """
    WelcomeModal {
        align: center middle;
    }

    WelcomeModal > Vertical {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    WelcomeModal .welcome-title {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }

    WelcomeModal .welcome-content {
        margin: 1 0;
    }

    WelcomeModal .button-bar {
        height: 3;
        align: center middle;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("enter", "dismiss_modal", "Get Started"),
        Binding("escape", "dismiss_modal", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Welcome to Gigsly!", classes="welcome-title")

            yield Static(
                """
Track your gigs, venues, payments, and booking outreach all in one place.

[bold]Quick Start:[/bold]

  [bold]v[/bold]  Add your first venue (where you play)
  [bold]n[/bold]  Add a show (from any screen)
  [bold]p[/bold]  Mark shows as paid when you get paid
  [bold]r[/bold]  See your action report

[bold]Navigation:[/bold]

  [bold]d[/bold]  Dashboard - overview and alerts
  [bold]v[/bold]  Venues - manage your venues
  [bold]s[/bold]  Shows - manage your gigs
  [bold]c[/bold]  Calendar - visual schedule

Press [bold]?[/bold] anytime for help.
""",
                classes="welcome-content",
            )

            with Vertical(classes="button-bar"):
                yield Button("Get Started", variant="primary", id="start")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "start":
            self.dismiss(True)

    def action_dismiss_modal(self) -> None:
        """Dismiss the modal."""
        self.dismiss(True)


async def show_welcome_if_first_run(app) -> None:
    """Show welcome modal if this is the user's first run.

    Checks if any venues exist. If not, shows the welcome modal.
    """
    from gigsly.db.session import get_session
    from gigsly.db import crud

    with get_session() as session:
        venues = crud.get_all_venues(session)
        if not venues:
            await app.push_screen_wait(WelcomeModal())
