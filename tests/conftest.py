"""Pytest fixtures for Gigsly tests."""

from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from gigsly.db.models import Base, ContactLog, RecurringGig, Show, Venue


@pytest.fixture
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_venues(test_db):
    """Create sample venues with varying attributes."""
    venues = [
        Venue(
            name="The Blue Note",
            location="Downtown",
            address="123 Jazz St",
            contact_name="Mike",
            contact_email="mike@bluenote.com",
            mileage_one_way=15.5,
            typical_pay=200.0,
            payment_method="check",
            requires_invoice=True,
            has_w9=True,
        ),
        Venue(
            name="Coffee House",
            location="Midtown",
            contact_name="Sarah",
            contact_phone="555-1234",
            mileage_one_way=8.0,
            typical_pay=75.0,
            payment_method="venmo",
            requires_invoice=False,
            has_w9=False,
        ),
        Venue(
            name="City Park Bandshell",
            location="Eastside",
            address="456 Park Ave",
            mileage_one_way=22.0,
            typical_pay=350.0,
            payment_method="direct_deposit",
            requires_invoice=True,
            has_w9=True,
            booking_window_start=1,
            booking_window_end=15,
        ),
    ]
    test_db.add_all(venues)
    test_db.commit()
    for v in venues:
        test_db.refresh(v)
    return venues


@pytest.fixture
def sample_shows(test_db, sample_venues):
    """Create sample shows covering past, future, paid, unpaid."""
    today = date.today()
    shows = [
        # Past paid show
        Show(
            venue_id=sample_venues[0].id,
            date=today - timedelta(days=30),
            pay_amount=200.0,
            payment_status="paid",
            payment_received_date=today - timedelta(days=25),
        ),
        # Past unpaid show (needs payment)
        Show(
            venue_id=sample_venues[0].id,
            date=today - timedelta(days=14),
            pay_amount=200.0,
            payment_status="pending",
            invoice_sent=True,
            invoice_sent_date=today - timedelta(days=13),
        ),
        # Future show
        Show(
            venue_id=sample_venues[1].id,
            date=today + timedelta(days=7),
            pay_amount=75.0,
            payment_status="pending",
        ),
        # Past show at venue requiring invoice (needs invoice)
        Show(
            venue_id=sample_venues[2].id,
            date=today - timedelta(days=5),
            pay_amount=350.0,
            payment_status="pending",
            invoice_sent=False,
        ),
    ]
    test_db.add_all(shows)
    test_db.commit()
    for s in shows:
        test_db.refresh(s)
    return shows


@pytest.fixture
def sample_recurring(test_db, sample_venues):
    """Create sample recurring gigs - weekly and monthly."""
    today = date.today()
    recurring = [
        RecurringGig(
            venue_id=sample_venues[0].id,
            pay_amount=200.0,
            pattern_type="weekly",
            day_of_week=4,  # Friday
            start_date=today - timedelta(days=60),
            is_active=True,
        ),
        RecurringGig(
            venue_id=sample_venues[2].id,
            pay_amount=350.0,
            pattern_type="monthly_date",
            day_of_month=15,
            start_date=today - timedelta(days=90),
            is_active=True,
        ),
    ]
    test_db.add_all(recurring)
    test_db.commit()
    for r in recurring:
        test_db.refresh(r)
    return recurring
