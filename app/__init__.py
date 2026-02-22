"""Donations CRM - Application factory."""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL",
            f"sqlite:///{os.path.join(app.instance_path, 'donations_crm.db')}",
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16 MB upload limit
        UPLOAD_FOLDER=os.path.join(app.instance_path, "uploads"),
        # SMTP defaults (override via .env or environment variables)
        SMTP_HOST=os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        SMTP_PORT=int(os.environ.get("SMTP_PORT", "587")),
        SMTP_USE_TLS=os.environ.get("SMTP_USE_TLS", "true").lower() == "true",
        SMTP_USERNAME=os.environ.get("SMTP_USERNAME", ""),
        SMTP_PASSWORD=os.environ.get("SMTP_PASSWORD", ""),
        SENDER_EMAIL=os.environ.get("SENDER_EMAIL", ""),
        SENDER_NAME=os.environ.get("SENDER_NAME", "Church Donations"),
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    # Ensure instance and upload folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    with app.app_context():
        from app.models import contact, donation, email_template, email_log  # noqa: F401
        db.create_all()
        _seed_default_template()

    # Register blueprints
    from app.routes import main, contacts, donations, email_templates, send_emails
    app.register_blueprint(main.bp)
    app.register_blueprint(contacts.bp)
    app.register_blueprint(donations.bp)
    app.register_blueprint(email_templates.bp)
    app.register_blueprint(send_emails.bp)

    return app


def _seed_default_template():
    """Insert a default email template if none exists."""
    from app.models.email_template import EmailTemplate
    if EmailTemplate.query.count() == 0:
        default = EmailTemplate(
            name="Year-End Donation Acknowledgement",
            subject="Your {{ year }} Donation to {{ church_name }}",
            body=(
                "Dear {{ first_name }} {{ last_name }},\n\n"
                "Thank you for your generous contributions to {{ church_name }} "
                "during {{ year }}.\n\n"
                "This letter serves as your official tax receipt for the calendar year "
                "{{ year }}. According to our records, your total charitable contribution "
                "for the year {{ year }} was ${{ '%.2f'|format(total_amount) }}.\n\n"
                "No goods or services were provided to you in exchange for these "
                "contributions. {{ church_name }} is a 501(c)(3) tax-exempt organization. "
                "Please retain this letter for your tax records.\n\n"
                "We are deeply grateful for your faith and generosity. Your support "
                "makes our mission possible.\n\n"
                "Blessings,\n"
                "{{ church_name }}\n"
            ),
            is_default=True,
        )
        db.session.add(default)
        db.session.commit()
