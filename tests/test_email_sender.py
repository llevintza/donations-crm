"""Tests for email sender service (render_template only, no SMTP)."""
import pytest
from jinja2 import TemplateSyntaxError

from app.services.email_sender import render_template


def test_render_basic():
    subject_tpl = "Your {{ year }} Donation to {{ church_name }}"
    body_tpl = "Dear {{ first_name }},\n\nThank you for donating ${{ '%.2f'|format(total_amount) }}."
    ctx = {
        "first_name": "John",
        "last_name": "Smith",
        "family_name": "Smith",
        "year": 2024,
        "church_name": "Hope Church",
        "total_amount": 500.0,
    }
    subject, body = render_template(subject_tpl, body_tpl, ctx)
    assert subject == "Your 2024 Donation to Hope Church"
    assert "John" in body
    assert "$500.00" in body


def test_render_format_amount():
    tpl = "{{ '%.2f'|format(total_amount) }}"
    subject, body = render_template(tpl, tpl, {"total_amount": 1234.5})
    assert subject == "1234.50"


def test_render_invalid_template():
    with pytest.raises(TemplateSyntaxError):
        render_template("{{ unclosed", "body", {})
