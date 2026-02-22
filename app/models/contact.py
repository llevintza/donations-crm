"""Contact model."""
from app import db


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    family_name = db.Column(db.String(200), nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    address = db.Column(db.String(500))

    def __repr__(self):
        return f"<Contact {self.family_name}>"
