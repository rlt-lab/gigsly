"""Tests for database models."""

from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from gigsly.db.models import Base, ContactLog, RecurringGig, Show, Venue


@pytest.fixture
def db_session():
    """Create an in-memory database session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


class TestVenueModel:
    def test_create_venue(self, db_session):
        venue = Venue(name="The Blue Note", location="Downtown")
        db_session.add(venue)
        db_session.commit()

        assert venue.id is not None
        assert venue.name == "The Blue Note"
        assert venue.requires_invoice is False
        assert venue.has_w9 is False

    def test_venue_with_all_fields(self, db_session):
        venue = Venue(
            name="Jazz Club",
            location="Midtown",
            address="123 Jazz St",
            contact_name="Mike",
            contact_email="mike@jazz.com",
            contact_phone="555-1234",
            mileage_one_way=15.5,
            typical_pay=200.0,
            payment_method="check",
            requires_invoice=True,
            has_w9=True,
            booking_window_start=1,
            booking_window_end=15,
            notes="Great venue!",
        )
        db_session.add(venue)
        db_session.commit()

        assert venue.payment_method == "check"
        assert venue.booking_window_start == 1
        assert venue.booking_window_end == 15

    def test_invalid_payment_method(self, db_session):
        with pytest.raises(ValueError, match="Invalid payment method"):
            Venue(name="Test", payment_method="bitcoin")


class TestShowModel:
    def test_create_show(self, db_session):
        venue = Venue(name="Test Venue")
        db_session.add(venue)
        db_session.commit()

        show = Show(venue_id=venue.id, date=date.today(), pay_amount=150.0)
        db_session.add(show)
        db_session.commit()

        assert show.id is not None
        assert show.payment_status == "pending"
        assert show.invoice_sent is False

    def test_show_display_name_with_venue(self, db_session):
        venue = Venue(name="The Blue Note")
        db_session.add(venue)
        db_session.commit()

        show = Show(venue_id=venue.id, date=date.today())
        db_session.add(show)
        db_session.commit()

        # Refresh to load relationship
        db_session.refresh(show)
        assert show.display_name == "The Blue Note"

    def test_show_display_name_orphaned(self, db_session):
        show = Show(
            venue_id=None,
            venue_name_snapshot="Deleted Venue",
            date=date.today() - timedelta(days=30),
        )
        db_session.add(show)
        db_session.commit()

        assert show.display_name == "Deleted Venue"

    def test_invalid_payment_status(self, db_session):
        venue = Venue(name="Test Venue")
        db_session.add(venue)
        db_session.commit()

        with pytest.raises(ValueError, match="Invalid payment status"):
            Show(venue_id=venue.id, date=date.today(), payment_status="invalid")


class TestRecurringGigModel:
    def test_create_weekly_gig(self, db_session):
        venue = Venue(name="Test Venue")
        db_session.add(venue)
        db_session.commit()

        gig = RecurringGig(
            venue_id=venue.id,
            pay_amount=200.0,
            pattern_type="weekly",
            day_of_week=4,  # Friday
            start_date=date.today(),
        )
        db_session.add(gig)
        db_session.commit()

        assert gig.id is not None
        assert gig.is_active is True

    def test_create_monthly_ordinal_gig(self, db_session):
        venue = Venue(name="Test Venue")
        db_session.add(venue)
        db_session.commit()

        gig = RecurringGig(
            venue_id=venue.id,
            pattern_type="monthly_ordinal",
            ordinal=2,  # Second
            day_of_week=1,  # Tuesday
            start_date=date.today(),
        )
        db_session.add(gig)
        db_session.commit()

        assert gig.ordinal == 2
        assert gig.day_of_week == 1

    def test_invalid_pattern_type(self, db_session):
        venue = Venue(name="Test Venue")
        db_session.add(venue)
        db_session.commit()

        with pytest.raises(ValueError, match="Invalid pattern type"):
            RecurringGig(
                venue_id=venue.id,
                pattern_type="invalid",
                start_date=date.today(),
            )


class TestContactLogModel:
    def test_create_contact_log(self, db_session):
        venue = Venue(name="Test Venue")
        db_session.add(venue)
        db_session.commit()

        log = ContactLog(
            venue_id=venue.id,
            contacted_at=datetime.now(),
            method="email",
            outcome="awaiting_response",
            notes="Sent booking inquiry",
        )
        db_session.add(log)
        db_session.commit()

        assert log.id is not None

    def test_contact_with_follow_up(self, db_session):
        venue = Venue(name="Test Venue")
        db_session.add(venue)
        db_session.commit()

        log = ContactLog(
            venue_id=venue.id,
            contacted_at=datetime.now(),
            method="phone",
            outcome="follow_up_needed",
            follow_up_date=date.today() + timedelta(days=7),
        )
        db_session.add(log)
        db_session.commit()

        assert log.follow_up_date == date.today() + timedelta(days=7)

    def test_invalid_contact_method(self, db_session):
        venue = Venue(name="Test Venue")
        db_session.add(venue)
        db_session.commit()

        with pytest.raises(ValueError, match="Invalid contact method"):
            ContactLog(
                venue_id=venue.id,
                contacted_at=datetime.now(),
                method="invalid",
            )


class TestRelationships:
    def test_venue_has_shows(self, db_session):
        venue = Venue(name="Test Venue")
        db_session.add(venue)
        db_session.commit()

        show1 = Show(venue_id=venue.id, date=date.today())
        show2 = Show(venue_id=venue.id, date=date.today() + timedelta(days=7))
        db_session.add_all([show1, show2])
        db_session.commit()

        db_session.refresh(venue)
        assert len(venue.shows) == 2

    def test_venue_has_contact_logs(self, db_session):
        venue = Venue(name="Test Venue")
        db_session.add(venue)
        db_session.commit()

        log = ContactLog(
            venue_id=venue.id, contacted_at=datetime.now(), method="email"
        )
        db_session.add(log)
        db_session.commit()

        db_session.refresh(venue)
        assert len(venue.contact_logs) == 1

    def test_recurring_gig_generates_shows(self, db_session):
        venue = Venue(name="Test Venue")
        db_session.add(venue)
        db_session.commit()

        gig = RecurringGig(
            venue_id=venue.id,
            pattern_type="weekly",
            day_of_week=4,
            start_date=date.today(),
        )
        db_session.add(gig)
        db_session.commit()

        # Add shows linked to recurring gig
        show = Show(
            venue_id=venue.id,
            recurring_gig_id=gig.id,
            date=date.today() + timedelta(days=7),
        )
        db_session.add(show)
        db_session.commit()

        db_session.refresh(gig)
        assert len(gig.shows) == 1
        assert gig.shows[0].recurring_gig_id == gig.id
