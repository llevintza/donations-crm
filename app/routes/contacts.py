"""Contacts routes."""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

from app import db
from app.models.contact import Contact
from app.services.contacts_import import parse_contacts_file

bp = Blueprint("contacts", __name__, url_prefix="/contacts")

ALLOWED_EXTENSIONS = {"xlsx", "xls", "csv"}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/")
def list_contacts():
    contacts = Contact.query.order_by(Contact.family_name).all()
    return render_template("contacts/list.html", contacts=contacts)


@bp.route("/upload", methods=["GET", "POST"])
def upload_contacts():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            flash("No file selected.", "danger")
            return redirect(request.url)
        if not _allowed(file.filename):
            flash("Only .xlsx, .xls, or .csv files are accepted.", "danger")
            return redirect(request.url)

        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        try:
            records = parse_contacts_file(filepath)
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(request.url)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

        replace = request.form.get("replace_existing") == "on"
        if replace:
            Contact.query.delete()

        added = 0
        for rec in records:
            # Upsert by family_name
            existing = Contact.query.filter(
                db.func.lower(Contact.family_name) == rec["family_name"].lower()
            ).first()
            if existing:
                existing.first_name = rec["first_name"]
                existing.last_name = rec["last_name"]
                existing.email = rec["email"]
                existing.address = rec["address"]
            else:
                db.session.add(Contact(**rec))
                added += 1

        db.session.commit()
        flash(
            f"Contacts imported successfully. {added} new, "
            f"{len(records) - added} updated.",
            "success",
        )
        return redirect(url_for("contacts.list_contacts"))

    return render_template("contacts/upload.html")


@bp.route("/<int:contact_id>/delete", methods=["POST"])
def delete_contact(contact_id: int):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    flash("Contact deleted.", "success")
    return redirect(url_for("contacts.list_contacts"))
