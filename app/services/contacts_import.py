"""Contacts import service.

Reads an Excel (.xlsx / .xls) or CSV file with contact information.

Expected columns (case-insensitive):
  - family_name  (required)
  - first_name   (required)
  - last_name    (required)
  - email        (required)
  - address      (optional)
"""
import pandas as pd

_FAMILY_ALIASES = {"family_name", "family name", "familyname", "family"}
_FIRST_ALIASES = {"first_name", "first name", "firstname", "first"}
_LAST_ALIASES = {"last_name", "last name", "lastname", "last"}
_EMAIL_ALIASES = {"email", "email_address", "email address", "e-mail"}
_ADDRESS_ALIASES = {"address", "mailing_address", "mailing address", "street"}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        lower = col.strip().lower()
        if lower in _FAMILY_ALIASES:
            rename_map[col] = "family_name"
        elif lower in _FIRST_ALIASES:
            rename_map[col] = "first_name"
        elif lower in _LAST_ALIASES:
            rename_map[col] = "last_name"
        elif lower in _EMAIL_ALIASES:
            rename_map[col] = "email"
        elif lower in _ADDRESS_ALIASES:
            rename_map[col] = "address"
    return df.rename(columns=rename_map)


def parse_contacts_file(filepath: str) -> list[dict]:
    """Parse a contacts Excel or CSV file and return a list of record dicts.

    Args:
        filepath: Absolute path to the uploaded file.

    Returns:
        List of dicts with keys: family_name, first_name, last_name, email, address.

    Raises:
        ValueError: If required columns are missing.
    """
    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)

    df = _normalize_columns(df)

    required = ["family_name", "first_name", "last_name", "email"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required column(s): {', '.join(missing)}. "
            "Required: family_name, first_name, last_name, email."
        )

    df = df.dropna(subset=required)

    records = []
    for _, row in df.iterrows():
        records.append(
            {
                "family_name": str(row["family_name"]).strip(),
                "first_name": str(row["first_name"]).strip(),
                "last_name": str(row["last_name"]).strip(),
                "email": str(row["email"]).strip(),
                "address": str(row.get("address", "")).strip() if "address" in df.columns else "",
            }
        )

    if not records:
        raise ValueError("No valid contact records found in the file.")

    return records
