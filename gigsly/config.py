"""Configuration management for Gigsly."""

import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w

# Default paths
GIGSLY_DIR = Path.home() / ".gigsly"
CONFIG_FILE = GIGSLY_DIR / "config.toml"
DATABASE_FILE = GIGSLY_DIR / "gigsly.db"
BACKUPS_DIR = GIGSLY_DIR / "backups"


@dataclass
class Settings:
    """Application settings with defaults."""

    # Payment thresholds
    overdue_days: int = 30  # Days after show before payment is "overdue"

    # Booking alerts
    booking_window_alert_days: int = 7  # Alert when window opens within N days
    low_show_count: int = 2  # "Low" upcoming shows threshold

    # Contact reminders
    contact_reminder_days: int = 60  # Remind to contact after N days
    awaiting_response_days: int = 14  # Suppress reminder while awaiting response

    # Tax/mileage
    home_address: str = ""
    irs_mileage_rates: dict = field(
        default_factory=lambda: {
            "2024": 0.67,
            "2025": 0.70,
            "2026": 0.70,
        }
    )

    @classmethod
    def load(cls) -> "Settings":
        """Load settings from config file, creating defaults if needed."""
        ensure_gigsly_dir()

        if not CONFIG_FILE.exists():
            settings = cls()
            settings.save()
            return settings

        with open(CONFIG_FILE, "rb") as f:
            data = tomllib.load(f)

        return cls(
            overdue_days=data.get("overdue_days", 30),
            booking_window_alert_days=data.get("booking_window_alert_days", 7),
            low_show_count=data.get("low_show_count", 2),
            contact_reminder_days=data.get("contact_reminder_days", 60),
            awaiting_response_days=data.get("awaiting_response_days", 14),
            home_address=data.get("home_address", ""),
            irs_mileage_rates=data.get("irs_mileage_rates", cls.irs_mileage_rates),
        )

    def save(self) -> None:
        """Save settings to config file."""
        ensure_gigsly_dir()

        data = {
            "overdue_days": self.overdue_days,
            "booking_window_alert_days": self.booking_window_alert_days,
            "low_show_count": self.low_show_count,
            "contact_reminder_days": self.contact_reminder_days,
            "awaiting_response_days": self.awaiting_response_days,
            "home_address": self.home_address,
            "irs_mileage_rates": self.irs_mileage_rates,
        }

        with open(CONFIG_FILE, "wb") as f:
            tomli_w.dump(data, f)

    def get_mileage_rate(self, year: int) -> float:
        """Get IRS mileage rate for a given year."""
        return self.irs_mileage_rates.get(str(year), 0.70)


def ensure_gigsly_dir() -> None:
    """Create ~/.gigsly/ directory if it doesn't exist."""
    GIGSLY_DIR.mkdir(exist_ok=True)
    BACKUPS_DIR.mkdir(exist_ok=True)


def get_database_url() -> str:
    """Get the SQLite database URL."""
    ensure_gigsly_dir()
    return f"sqlite:///{DATABASE_FILE}"
