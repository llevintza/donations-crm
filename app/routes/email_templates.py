"""Email template routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash

from app import db
from app.models.email_template import EmailTemplate
from app.services.email_sender import render_template as render_email

bp = Blueprint("email_templates", __name__, url_prefix="/templates")


@bp.route("/")
def list_templates():
    templates = EmailTemplate.query.order_by(EmailTemplate.name).all()
    return render_template("email_templates/list.html", templates=templates)


@bp.route("/new", methods=["GET", "POST"])
def new_template():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()
        is_default = request.form.get("is_default") == "on"

        if not name or not subject or not body:
            flash("Name, subject, and body are required.", "danger")
            return render_template(
                "email_templates/form.html",
                template=None,
                form_data=request.form,
            )

        if is_default:
            EmailTemplate.query.update({"is_default": False})

        tpl = EmailTemplate(name=name, subject=subject, body=body, is_default=is_default)
        db.session.add(tpl)
        db.session.commit()
        flash("Template created.", "success")
        return redirect(url_for("email_templates.list_templates"))

    return render_template("email_templates/form.html", template=None, form_data={})


@bp.route("/<int:tpl_id>/edit", methods=["GET", "POST"])
def edit_template(tpl_id: int):
    tpl = EmailTemplate.query.get_or_404(tpl_id)

    if request.method == "POST":
        tpl.name = request.form.get("name", "").strip()
        tpl.subject = request.form.get("subject", "").strip()
        tpl.body = request.form.get("body", "").strip()
        is_default = request.form.get("is_default") == "on"

        if not tpl.name or not tpl.subject or not tpl.body:
            flash("Name, subject, and body are required.", "danger")
            return render_template(
                "email_templates/form.html", template=tpl, form_data=request.form
            )

        if is_default:
            EmailTemplate.query.update({"is_default": False})
        tpl.is_default = is_default

        db.session.commit()
        flash("Template updated.", "success")
        return redirect(url_for("email_templates.list_templates"))

    return render_template("email_templates/form.html", template=tpl, form_data={})


@bp.route("/<int:tpl_id>/preview", methods=["GET", "POST"])
def preview_template(tpl_id: int):
    tpl = EmailTemplate.query.get_or_404(tpl_id)
    preview_subject = ""
    preview_body = ""
    error = ""

    sample_context = {
        "first_name": "Jane",
        "last_name": "Smith",
        "family_name": "Smith Family",
        "total_amount": 1250.00,
        "year": 2024,
        "church_name": "Our Lady of Hope Church",
    }

    from jinja2 import TemplateError
    try:
        preview_subject, preview_body = render_email(tpl.subject, tpl.body, sample_context)
    except TemplateError as exc:
        error = str(exc)

    return render_template(
        "email_templates/preview.html",
        template=tpl,
        preview_subject=preview_subject,
        preview_body=preview_body,
        error=error,
    )


@bp.route("/<int:tpl_id>/delete", methods=["POST"])
def delete_template(tpl_id: int):
    tpl = EmailTemplate.query.get_or_404(tpl_id)
    db.session.delete(tpl)
    db.session.commit()
    flash("Template deleted.", "success")
    return redirect(url_for("email_templates.list_templates"))
