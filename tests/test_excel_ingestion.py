"""Tests for Excel ingestion service."""
import io
import os
import pytest
import openpyxl

from app.services.excel_ingestion import parse_donations_file


def _write_xlsx(tmp_path, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    if rows:
        ws.append(list(rows[0].keys()))
        for row in rows:
            ws.append(list(row.values()))
    path = str(tmp_path / "donations.xlsx")
    wb.save(path)
    return path


def test_parse_basic(tmp_path):
    rows = [
        {"family_name": "Smith", "total_amount": 500.0},
        {"family_name": "Jones", "total_amount": 750.25},
    ]
    path = _write_xlsx(tmp_path, rows)
    records = parse_donations_file(path, default_year=2024)
    assert len(records) == 2
    assert records[0]["family_name"] == "Smith"
    assert records[0]["total_amount"] == 500.0
    assert records[0]["year"] == 2024


def test_parse_with_year_column(tmp_path):
    rows = [{"Family Name": "Adams", "Amount": 300.0, "Year": 2023}]
    path = _write_xlsx(tmp_path, rows)
    records = parse_donations_file(path, default_year=2024)
    assert records[0]["year"] == 2023
    assert records[0]["family_name"] == "Adams"


def test_parse_missing_family_name_column(tmp_path):
    rows = [{"total_amount": 100.0}]
    path = _write_xlsx(tmp_path, rows)
    with pytest.raises(ValueError, match="family_name"):
        parse_donations_file(path, default_year=2024)


def test_parse_missing_amount_column(tmp_path):
    rows = [{"family_name": "Test"}]
    path = _write_xlsx(tmp_path, rows)
    with pytest.raises(ValueError, match="total_amount"):
        parse_donations_file(path, default_year=2024)


def test_parse_csv(tmp_path):
    csv_path = str(tmp_path / "donations.csv")
    with open(csv_path, "w") as f:
        f.write("family_name,total_amount\nBrown,200\nGreen,400\n")
    records = parse_donations_file(csv_path, default_year=2024)
    assert len(records) == 2
    assert records[1]["family_name"] == "Green"


def test_parse_empty_rows_skipped(tmp_path):
    rows = [
        {"family_name": "Smith", "total_amount": 100.0},
        {"family_name": "", "total_amount": 200.0},  # empty family name
    ]
    path = _write_xlsx(tmp_path, rows)
    records = parse_donations_file(path, default_year=2024)
    assert len(records) == 1
