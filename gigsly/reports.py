"""CLI report generation for Gigsly."""

from datetime import date

from gigsly.algorithms import (
    assign_report_section,
    calculate_venue_score,
    payment_status_display,
    score_color,
    unpaid_balance,
)
from gigsly.db.crud import get_all_venues, get_shows_for_year, get_unpaid_shows
from gigsly.db.session import get_session


def print_smart_report() -> None:
    """Print smart report to terminal."""
    with get_session() as session:
        venues = get_all_venues(session)

        # Calculate scores and assign sections
        report_items: dict[str, list[tuple[int, str]]] = {
            "GET_PAID": [],
            "BOOK_SHOWS": [],
            "STAY_IN_TOUCH": [],
        }

        for venue in venues:
            score = calculate_venue_score(venue)
            section = assign_report_section(venue, score)
            if section:
                report_items[section].append((score, venue.name))

        # Sort each section by score (highest first)
        for section in report_items:
            report_items[section].sort(reverse=True)

        # Print report
        print("\n" + "=" * 60)
        print("GIGSLY SMART REPORT")
        print("=" * 60)

        # Get unpaid balance
        unpaid_shows = get_unpaid_shows(session)
        balance = unpaid_balance(unpaid_shows)
        if balance > 0:
            print(f"\nUnpaid Balance: ${balance:,.2f}")

        # Print sections
        section_names = {
            "GET_PAID": "1. GET PAID",
            "BOOK_SHOWS": "2. BOOK SHOWS",
            "STAY_IN_TOUCH": "3. STAY IN TOUCH",
        }

        for section_key, section_title in section_names.items():
            items = report_items[section_key]
            if items:
                print(f"\n{section_title}")
                print("-" * 40)
                for score, name in items:
                    color_indicator = {"red": "!", "yellow": "*", "green": " "}[
                        score_color(score)
                    ]
                    print(f"  {color_indicator} {name} (score: {score})")

        if not any(report_items.values()):
            print("\nAll caught up! No action items.")

        print("\n" + "=" * 60 + "\n")


def print_tax_report(year: int) -> None:
    """Print tax report to terminal."""
    with get_session() as session:
        shows = get_shows_for_year(session, year)

        # Separate by W-9 status
        w9_income = 0.0
        w9_venues = set()
        self_report_income = 0.0
        self_report_venues = set()
        total_mileage = 0.0

        for show in shows:
            if show.payment_status != "paid":
                continue

            amount = show.pay_amount or 0
            venue = show.venue

            if venue and venue.has_w9:
                w9_income += amount
                w9_venues.add(venue.name)
            else:
                self_report_income += amount
                if venue:
                    self_report_venues.add(venue.name)

            # Calculate mileage (round trip)
            if venue and venue.mileage_one_way:
                total_mileage += venue.mileage_one_way * 2

        # Get IRS mileage rate
        from gigsly.config import Settings

        settings = Settings.load()
        mileage_rate = settings.get_mileage_rate(year)
        mileage_deduction = total_mileage * mileage_rate

        # Print report
        print("\n" + "=" * 60)
        print(f"GIGSLY TAX REPORT - {year}")
        print("=" * 60)

        print(f"\nTotal Shows Paid: {len([s for s in shows if s.payment_status == 'paid'])}")
        print(f"Total Income: ${w9_income + self_report_income:,.2f}")

        print("\n--- INCOME BY W-9 STATUS ---")
        print(f"\n1099 Expected (W-9 on file): ${w9_income:,.2f}")
        if w9_venues:
            for v in sorted(w9_venues):
                print(f"   - {v}")

        print(f"\nSelf-Reported (No W-9): ${self_report_income:,.2f}")
        if self_report_venues:
            for v in sorted(self_report_venues):
                print(f"   - {v}")

        print("\n--- MILEAGE ---")
        print(f"Total Miles: {total_mileage:,.1f}")
        print(f"IRS Rate ({year}): ${mileage_rate}/mile")
        print(f"Estimated Deduction: ${mileage_deduction:,.2f}")

        print("\n" + "=" * 60 + "\n")
