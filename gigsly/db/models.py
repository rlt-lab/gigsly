"""SQLAlchemy models for Gigsly."""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, validates


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class PaymentMethod(str, Enum):
    """Payment method options."""

    CASH = "cash"
    CHECK = "check"
    VENMO = "venmo"
    CASHAPP = "cashapp"
    PAYPAL = "paypal"
    DIRECT_DEPOSIT = "direct_deposit"


class PaymentStatus(str, Enum):
    """Payment status options."""

    PENDING = "pending"
    PAID = "paid"


class PatternType(str, Enum):
    """Recurring gig pattern types."""

    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY_DATE = "monthly_date"
    MONTHLY_ORDINAL = "monthly_ordinal"
    CUSTOM = "custom"


class ContactMethod(str, Enum):
    """Contact method options."""

    EMAIL = "email"
    PHONE = "phone"
    IN_PERSON = "in_person"
    OTHER = "other"


class ContactOutcome(str, Enum):
    """Contact outcome options."""

    BOOKED = "booked"
    DECLINED = "declined"
    AWAITING_RESPONSE = "awaiting_response"
    FOLLOW_UP_NEEDED = "follow_up_needed"
    OTHER = "other"


class Venue(Base):
    """Venue model - locations where you perform."""

    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    address: Mapped[Optional[str]] = mapped_column(Text)
    contact_name: Mapped[Optional[str]] = mapped_column(String(255))
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    mileage_one_way: Mapped[Optional[float]] = mapped_column(Float)
    typical_pay: Mapped[Optional[float]] = mapped_column(Float)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    requires_invoice: Mapped[bool] = mapped_column(Boolean, default=False)
    has_w9: Mapped[bool] = mapped_column(Boolean, default=False)
    booking_window_start: Mapped[Optional[int]] = mapped_column(Integer)
    booking_window_end: Mapped[Optional[int]] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relationships
    shows: Mapped[list["Show"]] = relationship(
        "Show", back_populates="venue", cascade="all, delete-orphan"
    )
    recurring_gigs: Mapped[list["RecurringGig"]] = relationship(
        "RecurringGig", back_populates="venue", cascade="all, delete-orphan"
    )
    contact_logs: Mapped[list["ContactLog"]] = relationship(
        "ContactLog", back_populates="venue", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "booking_window_start IS NULL OR (booking_window_start >= 1 AND booking_window_start <= 31)",
            name="check_booking_window_start_range",
        ),
        CheckConstraint(
            "booking_window_end IS NULL OR (booking_window_end >= 1 AND booking_window_end <= 31)",
            name="check_booking_window_end_range",
        ),
        CheckConstraint(
            "mileage_one_way IS NULL OR mileage_one_way >= 0",
            name="check_mileage_non_negative",
        ),
        CheckConstraint(
            "payment_method IS NULL OR payment_method IN ('cash', 'check', 'venmo', 'cashapp', 'paypal', 'direct_deposit')",
            name="check_payment_method_enum",
        ),
    )

    @validates("payment_method")
    def validate_payment_method(self, key, value):
        if value is not None:
            valid = [m.value for m in PaymentMethod]
            if value not in valid:
                raise ValueError(f"Invalid payment method: {value}. Must be one of {valid}")
        return value


class Show(Base):
    """Show model - individual gig/performance record."""

    __tablename__ = "shows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    venue_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("venues.id"))
    recurring_gig_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("recurring_gigs.id")
    )
    venue_name_snapshot: Mapped[Optional[str]] = mapped_column(String(255))
    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[Optional[datetime]] = mapped_column(Time)
    end_time: Mapped[Optional[datetime]] = mapped_column(Time)
    pay_amount: Mapped[Optional[float]] = mapped_column(Float)
    payment_status: Mapped[str] = mapped_column(String(20), default="pending")
    payment_received_date: Mapped[Optional[date]] = mapped_column(Date)
    invoice_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    invoice_sent_date: Mapped[Optional[date]] = mapped_column(Date)
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relationships
    venue: Mapped[Optional["Venue"]] = relationship("Venue", back_populates="shows")
    recurring_gig: Mapped[Optional["RecurringGig"]] = relationship(
        "RecurringGig", back_populates="shows"
    )

    __table_args__ = (
        Index("show_venue_id_idx", "venue_id"),
        Index("show_date_idx", "date"),
        Index("show_recurring_gig_id_idx", "recurring_gig_id"),
        CheckConstraint(
            "payment_status IN ('pending', 'paid')",
            name="check_payment_status_enum",
        ),
        CheckConstraint(
            "invoice_sent = 0 OR invoice_sent_date IS NOT NULL",
            name="check_invoice_date_consistency",
        ),
        CheckConstraint(
            "payment_status = 'pending' OR payment_received_date IS NOT NULL",
            name="check_payment_date_consistency",
        ),
        CheckConstraint(
            "venue_id IS NOT NULL OR venue_name_snapshot IS NOT NULL",
            name="check_orphaned_shows_have_snapshot",
        ),
    )

    @validates("payment_status")
    def validate_payment_status(self, key, value):
        valid = [s.value for s in PaymentStatus]
        if value not in valid:
            raise ValueError(f"Invalid payment status: {value}. Must be one of {valid}")
        return value

    @property
    def display_name(self) -> str:
        """Return venue name, using snapshot for orphaned shows."""
        if self.venue:
            return self.venue.name
        return self.venue_name_snapshot or "Unknown Venue"


class RecurringGig(Base):
    """RecurringGig model - pattern definition for repeating shows."""

    __tablename__ = "recurring_gigs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    venue_id: Mapped[int] = mapped_column(Integer, ForeignKey("venues.id"), nullable=False)
    pay_amount: Mapped[Optional[float]] = mapped_column(Float)
    pattern_type: Mapped[str] = mapped_column(String(20), nullable=False)
    day_of_week: Mapped[Optional[int]] = mapped_column(Integer)
    day_of_month: Mapped[Optional[int]] = mapped_column(Integer)
    ordinal: Mapped[Optional[int]] = mapped_column(Integer)
    interval_weeks: Mapped[Optional[int]] = mapped_column(Integer)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relationships
    venue: Mapped["Venue"] = relationship("Venue", back_populates="recurring_gigs")
    shows: Mapped[list["Show"]] = relationship("Show", back_populates="recurring_gig")

    __table_args__ = (
        Index("recurring_gig_venue_id_idx", "venue_id"),
        CheckConstraint(
            "pattern_type IN ('weekly', 'biweekly', 'monthly_date', 'monthly_ordinal', 'custom')",
            name="check_pattern_type_enum",
        ),
        CheckConstraint(
            "day_of_week IS NULL OR (day_of_week >= 0 AND day_of_week <= 6)",
            name="check_day_of_week_range",
        ),
        CheckConstraint(
            "day_of_month IS NULL OR (day_of_month >= 1 AND day_of_month <= 31)",
            name="check_day_of_month_range",
        ),
        CheckConstraint(
            "ordinal IS NULL OR (ordinal >= 1 AND ordinal <= 5)",
            name="check_ordinal_range",
        ),
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="check_date_range",
        ),
    )

    @validates("pattern_type")
    def validate_pattern_type(self, key, value):
        valid = [p.value for p in PatternType]
        if value not in valid:
            raise ValueError(f"Invalid pattern type: {value}. Must be one of {valid}")
        return value


class ContactLog(Base):
    """ContactLog model - track outreach to venues."""

    __tablename__ = "contact_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    venue_id: Mapped[int] = mapped_column(Integer, ForeignKey("venues.id"), nullable=False)
    contacted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)
    outcome: Mapped[Optional[str]] = mapped_column(String(30))
    follow_up_date: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationships
    venue: Mapped["Venue"] = relationship("Venue", back_populates="contact_logs")

    __table_args__ = (
        Index("contact_log_venue_id_idx", "venue_id"),
        CheckConstraint(
            "method IN ('email', 'phone', 'in_person', 'other')",
            name="check_contact_method_enum",
        ),
        CheckConstraint(
            "outcome IS NULL OR outcome IN ('booked', 'declined', 'awaiting_response', 'follow_up_needed', 'other')",
            name="check_contact_outcome_enum",
        ),
    )

    @validates("method")
    def validate_method(self, key, value):
        valid = [m.value for m in ContactMethod]
        if value not in valid:
            raise ValueError(f"Invalid contact method: {value}. Must be one of {valid}")
        return value

    @validates("outcome")
    def validate_outcome(self, key, value):
        if value is not None:
            valid = [o.value for o in ContactOutcome]
            if value not in valid:
                raise ValueError(f"Invalid contact outcome: {value}. Must be one of {valid}")
        return value
