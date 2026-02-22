"""Cross-reference service.

Matches donation records to contacts by family_name (case-insensitive, stripped).
"""
from app.models.contact import Contact
from app.models.donation import Donation


def build_mailing_list(year: int) -> list[dict]:
    """Return a list of merged records for the given year.

    Each record has:
        family_name, first_name, last_name, email, address, total_amount, year,
        matched (bool)

    Unmatched donations are included with matched=False so the user can
    review them.
    """
    donations = Donation.query.filter_by(year=year).all()
    contacts = Contact.query.all()

    # Build lookup: normalised family name -> contact
    contact_map: dict[str, Contact] = {
        _key(c.family_name): c for c in contacts
    }

    results = []
    for donation in donations:
        key = _key(donation.family_name)
        contact = contact_map.get(key)
        results.append(
            {
                "donation_id": donation.id,
                "family_name": donation.family_name,
                "total_amount": donation.total_amount,
                "year": donation.year,
                "matched": contact is not None,
                "first_name": contact.first_name if contact else "",
                "last_name": contact.last_name if contact else "",
                "email": contact.email if contact else "",
                "address": contact.address if contact else "",
            }
        )

    return results


def _key(name: str) -> str:
    return name.strip().lower()
