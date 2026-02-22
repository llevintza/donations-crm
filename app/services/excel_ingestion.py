"""Excel ingestion service.

Reads an Excel (.xlsx / .xls) or CSV file with donation data.

Expected columns (case-insensitive, extra columns ignored):
  - family_name  (or "Family Name", "family name", etc.)
  - total_amount (or "Total Amount", "Amount", "Total", etc.)
  - year         (optional; falls back to provided `default_year`)
"""
import pandas as pd


# Map of accepted column aliases -> canonical name
_FAMILY_ALIASES = {"family_name", "family name", "familyname", "family"}
_AMOUNT_ALIASES = {"total_amount", "total amount", "amount", "total", "donation"}
_YEAR_ALIASES = {"year", "donation_year", "donation year"}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to canonical names based on aliases."""
    rename_map = {}
    for col in df.columns:
        lower = col.strip().lower()
        if lower in _FAMILY_ALIASES:
            rename_map[col] = "family_name"
        elif lower in _AMOUNT_ALIASES:
            rename_map[col] = "total_amount"
        elif lower in _YEAR_ALIASES:
            rename_map[col] = "year"
    return df.rename(columns=rename_map)


def parse_donations_file(filepath: str, default_year: int) -> list[dict]:
    """Parse a donations Excel or CSV file and return a list of record dicts.

    Args:
        filepath: Absolute path to the uploaded file.
        default_year: Year to use when the file doesn't include a year column.

    Returns:
        List of dicts with keys: family_name, total_amount, year.

    Raises:
        ValueError: If required columns are missing or data is invalid.
    """
    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)

    df = _normalize_columns(df)

    if "family_name" not in df.columns:
        raise ValueError(
            "Missing required column: 'family_name'. "
            "Accepted aliases: family_name, family name, familyname, family."
        )
    if "total_amount" not in df.columns:
        raise ValueError(
            "Missing required column: 'total_amount'. "
            "Accepted aliases: total_amount, total amount, amount, total, donation."
        )

    if "year" not in df.columns:
        df["year"] = default_year

    # Drop rows with missing family name or amount
    df = df.dropna(subset=["family_name", "total_amount"])

    records = []
    for _, row in df.iterrows():
        family_name = str(row["family_name"]).strip()
        if not family_name:
            continue
        try:
            total_amount = float(row["total_amount"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid total_amount for family '{family_name}': {row['total_amount']}"
            ) from exc
        try:
            year = int(row["year"])
        except (TypeError, ValueError):
            year = default_year
        records.append(
            {"family_name": family_name, "total_amount": total_amount, "year": year}
        )

    if not records:
        raise ValueError("No valid donation records found in the file.")

    return records
