"""Email sending service."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, BaseLoader, TemplateSyntaxError

from app import db
from app.models.email_log import EmailLog


def render_template(subject_tpl: str, body_tpl: str, context: dict) -> tuple[str, str]:
    """Render subject and body Jinja2 templates with the given context.

    Args:
        subject_tpl: Jinja2 template string for the subject.
        body_tpl: Jinja2 template string for the body.
        context: Dictionary of variables available in templates.

    Returns:
        Tuple of (rendered_subject, rendered_body).

    Raises:
        TemplateSyntaxError: If either template has a syntax error.
    """
    env = Environment(loader=BaseLoader())
    rendered_subject = env.from_string(subject_tpl).render(**context)
    rendered_body = env.from_string(body_tpl).render(**context)
    return rendered_subject, rendered_body


def send_email(
    smtp_host: str,
    smtp_port: int,
    use_tls: bool,
    username: str,
    password: str,
    sender_email: str,
    sender_name: str,
    recipient_email: str,
    subject: str,
    body: str,
) -> None:
    """Send a single plain-text email via SMTP.

    Raises:
        smtplib.SMTPException: On SMTP errors.
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = recipient_email
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if use_tls:
            server.starttls()
        if username and password:
            server.login(username, password)
        server.sendmail(sender_email, [recipient_email], msg.as_string())


def send_donation_emails(
    mailing_list: list[dict],
    subject_tpl: str,
    body_tpl: str,
    church_name: str,
    smtp_host: str,
    smtp_port: int,
    use_tls: bool,
    username: str,
    password: str,
    sender_email: str,
    sender_name: str,
) -> dict:
    """Send year-end donation emails to all matched records.

    Args:
        mailing_list: Output of crossref.build_mailing_list() filtered to matched=True.
        subject_tpl / body_tpl: Jinja2 template strings.
        church_name: Used in templates as {{ church_name }}.
        smtp_*: SMTP connection settings.
        sender_email / sender_name: From address.

    Returns:
        dict with keys 'sent' (int), 'failed' (int), 'errors' (list of str).
    """
    sent = 0
    failed = 0
    errors = []

    for record in mailing_list:
        if not record.get("matched"):
            continue

        context = {
            "first_name": record["first_name"],
            "last_name": record["last_name"],
            "family_name": record["family_name"],
            "total_amount": record["total_amount"],
            "year": record["year"],
            "church_name": church_name,
        }

        try:
            subject, body = render_template(subject_tpl, body_tpl, context)
            send_email(
                smtp_host=smtp_host,
                smtp_port=smtp_port,
                use_tls=use_tls,
                username=username,
                password=password,
                sender_email=sender_email,
                sender_name=sender_name,
                recipient_email=record["email"],
                subject=subject,
                body=body,
            )
            log = EmailLog(
                family_name=record["family_name"],
                recipient_email=record["email"],
                subject=subject,
                year=record["year"],
                status="sent",
            )
            sent += 1
        except Exception as exc:  # noqa: BLE001  # broad catch keeps batch running
            error_msg = str(exc)
            log = EmailLog(
                family_name=record["family_name"],
                recipient_email=record["email"],
                subject="",
                year=record["year"],
                status="failed",
                error_message=error_msg,
            )
            failed += 1
            errors.append(f"{record['family_name']} <{record['email']}>: {error_msg}")

        db.session.add(log)

    db.session.commit()
    return {"sent": sent, "failed": failed, "errors": errors}
