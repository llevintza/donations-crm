"""EmailTemplate model."""
from app import db


class EmailTemplate(db.Model):
    __tablename__ = "email_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<EmailTemplate {self.name}>"
