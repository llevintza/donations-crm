"""Donations routes."""
import os
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

from app import db
from app.models.donation import Donation
from app.services.excel_ingestion import parse_donations_file

bp = Blueprint("donations", __name__, url_prefix="/donations")

ALLOWED_EXTENSIONS = {"xlsx", "xls", "csv"}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/")
def list_donations():
    year = request.args.get("year", type=int)
    query = Donation.query.order_by(Donation.year.desc(), Donation.family_name)
    if year:
        query = query.filter_by(year=year)
    donations = query.all()
    years = [
        r[0]
        for r in Donation.query.with_entities(Donation.year)
        .distinct()
        .order_by(Donation.year.desc())
        .all()
    ]
    return render_template("donations/list.html", donations=donations, years=years, selected_year=year)


@bp.route("/upload", methods=["GET", "POST"])
def upload_donations():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            flash("No file selected.", "danger")
            return redirect(request.url)
        if not _allowed(file.filename):
            flash("Only .xlsx, .xls, or .csv files are accepted.", "danger")
            return redirect(request.url)

        default_year = request.form.get("default_year", type=int, default=datetime.now().year - 1)
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        try:
            records = parse_donations_file(filepath, default_year=default_year)
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(request.url)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

        replace = request.form.get("replace_existing") == "on"
        if replace:
            year_to_clear = records[0]["year"] if records else default_year
            Donation.query.filter_by(year=year_to_clear).delete()

        added = 0
        for rec in records:
            existing = Donation.query.filter(
                db.func.lower(Donation.family_name) == rec["family_name"].lower(),
                Donation.year == rec["year"],
            ).first()
            if existing:
                existing.total_amount = rec["total_amount"]
            else:
                db.session.add(Donation(**rec))
                added += 1

        db.session.commit()
        actual_years = sorted({r["year"] for r in records})
        year_str = ", ".join(str(y) for y in actual_years)
        flash(
            f"Donations imported for year(s) {year_str}. "
            f"{added} new, {len(records) - added} updated.",
            "success",
        )
        return redirect(url_for("donations.list_donations"))

    current_year = datetime.now().year
    return render_template("donations/upload.html", default_year=current_year - 1)
