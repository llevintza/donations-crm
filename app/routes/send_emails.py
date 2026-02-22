"""Send emails routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

from app.models.donation import Donation
from app.models.email_template import EmailTemplate
from app.models.email_log import EmailLog
from app.services.crossref import build_mailing_list
from app.services.email_sender import send_donation_emails

bp = Blueprint("send_emails", __name__, url_prefix="/send")


@bp.route("/", methods=["GET"])
def send_index():
    years = [
        r[0]
        for r in Donation.query.with_entities(Donation.year)
        .distinct()
        .order_by(Donation.year.desc())
        .all()
    ]
    templates = EmailTemplate.query.order_by(EmailTemplate.name).all()
    default_template = EmailTemplate.query.filter_by(is_default=True).first()
    return render_template(
        "send/index.html",
        years=years,
        templates=templates,
        default_template=default_template,
    )


@bp.route("/preview", methods=["GET", "POST"])
def preview():
    year = request.args.get("year", type=int) or request.form.get("year", type=int)
    tpl_id = request.args.get("template_id", type=int) or request.form.get(
        "template_id", type=int
    )

    if not year or not tpl_id:
        flash("Please select a year and a template.", "warning")
        return redirect(url_for("send_emails.send_index"))

    mailing_list = build_mailing_list(year)
    template = EmailTemplate.query.get_or_404(tpl_id)

    matched = [r for r in mailing_list if r["matched"]]
    unmatched = [r for r in mailing_list if not r["matched"]]

    return render_template(
        "send/preview.html",
        year=year,
        template=template,
        matched=matched,
        unmatched=unmatched,
    )


@bp.route("/send", methods=["POST"])
def do_send():
    year = request.form.get("year", type=int)
    tpl_id = request.form.get("template_id", type=int)
    church_name = request.form.get("church_name", "").strip() or "Our Church"

    if not year or not tpl_id:
        flash("Year and template are required.", "danger")
        return redirect(url_for("send_emails.send_index"))

    template = EmailTemplate.query.get_or_404(tpl_id)
    mailing_list = build_mailing_list(year)

    result = send_donation_emails(
        mailing_list=mailing_list,
        subject_tpl=template.subject,
        body_tpl=template.body,
        church_name=church_name,
        smtp_host=current_app.config["SMTP_HOST"],
        smtp_port=current_app.config["SMTP_PORT"],
        use_tls=current_app.config["SMTP_USE_TLS"],
        username=current_app.config["SMTP_USERNAME"],
        password=current_app.config["SMTP_PASSWORD"],
        sender_email=current_app.config["SENDER_EMAIL"],
        sender_name=current_app.config["SENDER_NAME"],
    )

    flash(
        f"Done! {result['sent']} email(s) sent, {result['failed']} failed.",
        "success" if result["failed"] == 0 else "warning",
    )
    if result["errors"]:
        for err in result["errors"]:
            flash(err, "danger")

    return redirect(url_for("send_emails.send_index"))


@bp.route("/logs")
def logs():
    year = request.args.get("year", type=int)
    query = EmailLog.query.order_by(EmailLog.sent_at.desc())
    if year:
        query = query.filter_by(year=year)
    email_logs = query.all()
    years = [
        r[0]
        for r in EmailLog.query.with_entities(EmailLog.year)
        .distinct()
        .order_by(EmailLog.year.desc())
        .all()
    ]
    return render_template("send/logs.html", email_logs=email_logs, years=years, selected_year=year)
