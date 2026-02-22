"""EmailLog model."""
from datetime import datetime
from app import db


class EmailLog(db.Model):
    __tablename__ = "email_logs"

    id = db.Column(db.Integer, primary_key=True)
    family_name = db.Column(db.String(200))
    recipient_email = db.Column(db.String(254))
    subject = db.Column(db.String(500))
    year = db.Column(db.Integer)
    status = db.Column(db.String(20), default="sent")  # "sent" | "failed"
    error_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())

    def __repr__(self):
        return f"<EmailLog {self.recipient_email} {self.status}>"
