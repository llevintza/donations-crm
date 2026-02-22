"""Tests for cross-reference service."""
import pytest

from app import db
from app.models.contact import Contact
from app.models.donation import Donation
from app.services.crossref import build_mailing_list


def test_build_mailing_list_matched(app):
    with app.app_context():
        db.create_all()
        db.session.add(Contact(
            family_name="Smith Family",
            first_name="John",
            last_name="Smith",
            email="john@example.com",
        ))
        db.session.add(Donation(family_name="Smith Family", total_amount=500.0, year=2024))
        db.session.commit()

        result = build_mailing_list(2024)
        matched = [r for r in result if r["matched"]]
        assert len(matched) == 1
        assert matched[0]["email"] == "john@example.com"
        assert matched[0]["total_amount"] == 500.0

        db.session.remove()
        db.drop_all()


def test_build_mailing_list_case_insensitive(app):
    with app.app_context():
        db.create_all()
        db.session.add(Contact(
            family_name="JONES FAMILY",
            first_name="Mary",
            last_name="Jones",
            email="mary@example.com",
        ))
        db.session.add(Donation(family_name="jones family", total_amount=300.0, year=2024))
        db.session.commit()

        result = build_mailing_list(2024)
        matched = [r for r in result if r["matched"]]
        assert len(matched) == 1
        assert matched[0]["first_name"] == "Mary"

        db.session.remove()
        db.drop_all()


def test_build_mailing_list_unmatched(app):
    with app.app_context():
        db.create_all()
        db.session.add(Donation(family_name="Unknown Family", total_amount=100.0, year=2024))
        db.session.commit()

        result = build_mailing_list(2024)
        unmatched = [r for r in result if not r["matched"]]
        assert len(unmatched) == 1
        assert unmatched[0]["family_name"] == "Unknown Family"

        db.session.remove()
        db.drop_all()
