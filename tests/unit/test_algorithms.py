"""Tests for core algorithms."""

from datetime import date, datetime, timedelta

import pytest

from gigsly.algorithms import (
    days_between,
    days_since_contact,
    days_until_booking_window,
    is_booking_window_open,
    iter_monthly_date,
    iter_monthly_ordinal,
    iter_weekly,
    nth_weekday_of_month,
    payment_status_display,
    should_suppress_contact_reminder,
)
from gigsly.db.models import ContactLog, Show, Venue


class TestDaysBetween:
    def test_same_day(self):
        d = date(2025, 1, 15)
        assert days_between(d, d) == 0

    def test_one_day_apart(self):
        d1 = date(2025, 1, 15)
        d2 = date(2025, 1, 16)
        assert days_between(d1, d2) == 1

    def test_negative_days(self):
        d1 = date(2025, 1, 16)
        d2 = date(2025, 1, 15)
        assert days_between(d1, d2) == -1


class TestBookingWindow:
    def test_no_window_configured(self):
        venue = Venue(name="Test", booking_window_start=None)
        assert is_booking_window_open(venue) is False
        assert days_until_booking_window(venue) is None

    def test_window_currently_open(self):
        today = date.today()
        venue = Venue(
            name="Test",
            booking_window_start=today.day,
            booking_window_end=today.day,
        )
        assert is_booking_window_open(venue) is True
        assert days_until_booking_window(venue) is None


class TestPaymentStatus:
    def test_paid_show(self):
        show = Show(
            date=date.today() - timedelta(days=30),
            payment_status="paid",
            payment_received_date=date.today() - timedelta(days=25),
        )
        text, color = payment_status_display(show)
        assert text == "paid"
        assert color == "green"

    def test_future_show_pending(self):
        show = Show(date=date.today() + timedelta(days=7), payment_status="pending")
        text, color = payment_status_display(show)
        assert text == "pending"
        assert color == "gray"

    def test_past_show_unpaid(self):
        show = Show(date=date.today() - timedelta(days=10), payment_status="pending")
        text, color = payment_status_display(show)
        assert "UNPAID" in text
        assert "10d" in text
        assert color == "yellow"

    def test_past_show_overdue(self):
        show = Show(date=date.today() - timedelta(days=45), payment_status="pending")
        text, color = payment_status_display(show)
        assert "OVERDUE" in text
        assert "45d" in text
        assert color == "red"


class TestNthWeekdayOfMonth:
    def test_first_monday_jan_2025(self):
        # January 2025 starts on Wednesday, so first Monday is 6th
        result = nth_weekday_of_month(1, 0, date(2025, 1, 1))
        assert result == date(2025, 1, 6)

    def test_third_friday_jan_2025(self):
        # January 2025: Fridays are 3, 10, 17, 24, 31
        result = nth_weekday_of_month(3, 4, date(2025, 1, 1))
        assert result == date(2025, 1, 17)

    def test_fifth_friday_feb_2025(self):
        # February 2025 doesn't have a 5th Friday
        result = nth_weekday_of_month(5, 4, date(2025, 2, 1))
        assert result is None


class TestIterWeekly:
    def test_weekly_fridays(self):
        start = date(2025, 1, 1)
        end = date(2025, 1, 31)
        pattern_start = date(2025, 1, 3)  # A Friday

        results = list(iter_weekly(pattern_start, 4, start, end))
        # Fridays in Jan 2025: 3, 10, 17, 24, 31
        assert len(results) == 5
        assert results[0] == date(2025, 1, 3)
        assert results[-1] == date(2025, 1, 31)

    def test_biweekly(self):
        start = date(2025, 1, 1)
        end = date(2025, 1, 31)
        pattern_start = date(2025, 1, 3)

        results = list(iter_weekly(pattern_start, 4, start, end, interval=2))
        # Every other Friday from Jan 3: 3, 17, 31
        assert len(results) == 3


class TestIterMonthlyDate:
    def test_15th_of_month(self):
        start = date(2025, 1, 1)
        end = date(2025, 3, 31)

        results = list(iter_monthly_date(15, start, end))
        assert len(results) == 3
        assert results == [date(2025, 1, 15), date(2025, 2, 15), date(2025, 3, 15)]

    def test_31st_handles_short_months(self):
        start = date(2025, 1, 1)
        end = date(2025, 3, 31)

        results = list(iter_monthly_date(31, start, end))
        assert len(results) == 3
        assert results[0] == date(2025, 1, 31)
        assert results[1] == date(2025, 2, 28)  # Feb doesn't have 31
        assert results[2] == date(2025, 3, 31)


class TestIterMonthlyOrdinal:
    def test_second_tuesday(self):
        start = date(2025, 1, 1)
        end = date(2025, 3, 31)

        results = list(iter_monthly_ordinal(2, 1, start, end))
        assert len(results) == 3
        assert results[0] == date(2025, 1, 14)  # 2nd Tuesday of Jan 2025
        assert results[1] == date(2025, 2, 11)  # 2nd Tuesday of Feb 2025
        assert results[2] == date(2025, 3, 11)  # 2nd Tuesday of Mar 2025


class TestContactReminders:
    def test_no_contacts_returns_none(self):
        venue = Venue(name="Test")
        venue.contact_logs = []
        assert days_since_contact(venue) is None

    def test_awaiting_response_suppresses(self):
        venue = Venue(name="Test")
        venue.contact_logs = [
            ContactLog(
                venue_id=1,
                contacted_at=datetime.now() - timedelta(days=5),
                method="email",
                outcome="awaiting_response",
            )
        ]
        assert should_suppress_contact_reminder(venue) is True

    def test_old_awaiting_response_does_not_suppress(self):
        venue = Venue(name="Test")
        venue.contact_logs = [
            ContactLog(
                venue_id=1,
                contacted_at=datetime.now() - timedelta(days=20),
                method="email",
                outcome="awaiting_response",
            )
        ]
        assert should_suppress_contact_reminder(venue) is False

    def test_future_followup_suppresses(self):
        venue = Venue(name="Test")
        venue.contact_logs = [
            ContactLog(
                venue_id=1,
                contacted_at=datetime.now() - timedelta(days=30),
                method="email",
                outcome="booked",
                follow_up_date=date.today() + timedelta(days=7),
            )
        ]
        assert should_suppress_contact_reminder(venue) is True
