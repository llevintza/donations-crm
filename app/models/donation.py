"""Donation model."""
from app import db


class Donation(db.Model):
    __tablename__ = "donations"

    id = db.Column(db.Integer, primary_key=True)
    family_name = db.Column(db.String(200), nullable=False, index=True)
    total_amount = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Donation {self.family_name} ${self.total_amount} ({self.year})>"
