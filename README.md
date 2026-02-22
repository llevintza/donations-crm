# donations-crm

A simple CRM application for sending year-end tax-acknowledgement emails to church/non-profit donors.

## Features

- **Upload donation data** from an Excel (`.xlsx`/`.xls`) or CSV file produced by your accounting department.
- **Upload contact information** from a separate Excel/CSV file to get donor email addresses.
- **Automatic cross-referencing** – donation records are matched to contacts by family name (case-insensitive).
- **Jinja2 email templates** – customise the subject and body with per-donor variables.
- **One-click send** – preview the mailing list, review unmatched records, and send emails via SMTP.
- **Email log** – every send attempt (success or failure) is recorded for auditing.

---

## Quick Start

### 1. Clone & install dependencies

```bash
git clone https://github.com/llevintza/donations-crm.git
cd donations-crm
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure SMTP

Copy `.env.example` to `.env` and fill in your SMTP credentials:

```bash
cp .env.example .env
```

```dotenv
SECRET_KEY=change-me-in-production

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=Church Donations
```

> **Gmail tip:** use an [App Password](https://support.google.com/accounts/answer/185833) instead of your account password.

### 3. Run the application

```bash
flask --app wsgi:app run
# Open http://127.0.0.1:5000
```

---

## Workflow

1. **Upload Contacts** – go to *Contacts → Upload Contacts File* and import your contact spreadsheet.
2. **Upload Donations** – go to *Donations → Upload Donations File* and import the accounting Excel export.
3. **Review Templates** – go to *Templates* to edit the default year-end template or create a new one.
4. **Send Emails** – go to *Send Emails*, pick a year and template, review the mailing list, enter your church name, and click **Send**.
5. **Check Logs** – go to *Email Logs* to review what was sent and any failures.

---

## File Formats

### Contacts file

| Column | Required | Accepted aliases |
|--------|----------|-----------------|
| `family_name` | ✅ | `family name`, `familyname`, `family` |
| `first_name` | ✅ | `first name`, `firstname`, `first` |
| `last_name` | ✅ | `last name`, `lastname`, `last` |
| `email` | ✅ | `email address`, `e-mail` |
| `address` | ❌ | `mailing address`, `street` |

### Donations file

| Column | Required | Accepted aliases |
|--------|----------|-----------------|
| `family_name` | ✅ | `family name`, `familyname`, `family` |
| `total_amount` | ✅ | `total amount`, `amount`, `total`, `donation` |
| `year` | ❌ (uses *Default Year*) | `donation year`, `donation_year` |

---

## Email Template Variables

| Variable | Description |
|----------|-------------|
| `{{ first_name }}` | Donor's first name |
| `{{ last_name }}` | Donor's last name |
| `{{ family_name }}` | Family name from donation record |
| `{{ total_amount }}` | Total donation amount (float) |
| `{{ year }}` | Donation year |
| `{{ church_name }}` | Entered at send time |

Use standard Jinja2 syntax. Example for currency formatting:

```
${{ "%.2f"|format(total_amount) }}
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Project Structure

```
donations-crm/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # Flask blueprints
│   ├── services/            # Business logic
│   │   ├── excel_ingestion.py
│   │   ├── contacts_import.py
│   │   ├── crossref.py
│   │   └── email_sender.py
│   └── templates/           # Jinja2 HTML templates
├── tests/                   # pytest test suite
├── wsgi.py                  # Entry point
├── requirements.txt
└── .env.example
```
