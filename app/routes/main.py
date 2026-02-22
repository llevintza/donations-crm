"""Main / dashboard routes."""
from flask import Blueprint, render_template

from app.models.contact import Contact
from app.models.donation import Donation
from app.models.email_log import EmailLog

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    total_contacts = Contact.query.count()
    total_donations = Donation.query.count()
    donation_years = (
        Donation.query.with_entities(Donation.year).distinct().order_by(Donation.year.desc()).all()
    )
    recent_logs = (
        EmailLog.query.order_by(EmailLog.sent_at.desc()).limit(10).all()
    )
    return render_template(
        "index.html",
        total_contacts=total_contacts,
        total_donations=total_donations,
        donation_years=[r[0] for r in donation_years],
        recent_logs=recent_logs,
    )
