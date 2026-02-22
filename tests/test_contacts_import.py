"""Tests for contacts import service."""
import openpyxl
import pytest

from app.services.contacts_import import parse_contacts_file


def _write_xlsx(tmp_path, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    if rows:
        ws.append(list(rows[0].keys()))
        for row in rows:
            ws.append(list(row.values()))
    path = str(tmp_path / "contacts.xlsx")
    wb.save(path)
    return path


def test_parse_basic(tmp_path):
    rows = [
        {
            "family_name": "Smith",
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@example.com",
        }
    ]
    path = _write_xlsx(tmp_path, rows)
    records = parse_contacts_file(path)
    assert len(records) == 1
    assert records[0]["email"] == "john@example.com"


def test_parse_with_address(tmp_path):
    rows = [
        {
            "family_name": "Jones",
            "first_name": "Alice",
            "last_name": "Jones",
            "email": "alice@example.com",
            "address": "123 Main St",
        }
    ]
    path = _write_xlsx(tmp_path, rows)
    records = parse_contacts_file(path)
    assert records[0]["address"] == "123 Main St"


def test_parse_alias_columns(tmp_path):
    rows = [
        {
            "Family Name": "Brown",
            "First Name": "Bob",
            "Last Name": "Brown",
            "Email Address": "bob@example.com",
        }
    ]
    path = _write_xlsx(tmp_path, rows)
    records = parse_contacts_file(path)
    assert records[0]["family_name"] == "Brown"


def test_parse_missing_required_column(tmp_path):
    rows = [{"family_name": "Smith", "first_name": "John", "last_name": "Smith"}]
    path = _write_xlsx(tmp_path, rows)
    with pytest.raises(ValueError, match="email"):
        parse_contacts_file(path)


def test_parse_csv(tmp_path):
    csv_path = str(tmp_path / "contacts.csv")
    with open(csv_path, "w") as f:
        f.write("family_name,first_name,last_name,email\nDoe,Jane,Doe,jane@example.com\n")
    records = parse_contacts_file(csv_path)
    assert len(records) == 1
    assert records[0]["first_name"] == "Jane"
