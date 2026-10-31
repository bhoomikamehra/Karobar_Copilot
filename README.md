# Karobar Copilot 🧾

An AI-assisted invoice and back-office assistant for small shop owners and traders in India.

Small businesses receive supplier invoices as paper, WhatsApp photos and PDFs, then spend hours typing them into registers or Excel. Mistakes creep in, payments get missed, and GST details are hard to prepare at month end. Karobar Copilot turns an uploaded invoice into structured data, lets the owner review it, and then updates stock, payments and the GST summary.


## How it works

1. **Upload** an invoice (photo or PDF).
2. **Read:** the invoice details are extracted: vendor, invoice number, dates, line items, rates and GST.
3. **Review:** the owner checks and edits everything. Nothing is saved without approval.
4. **Approve:** the system saves the invoice and updates stock automatically.
5. **Track:** payments (paid, pending, overdue), GST totals and a business dashboard stay up to date.

## Features

- Invoice upload with an editable review screen
- Human approval before anything is saved
- Duplicate invoice detection
- Automatic inventory updates
- Payment tracker with overdue reminders
- GST summary (taxable value, total GST, CGST and SGST)
- Dashboard with charts: monthly spend, payment status, vendor-wise spend, top inventory items
- Insights card that flags overdue invoices and GST liability

## Current status

This is a working prototype. The invoice reading step in `extract.py` currently returns **sample invoice data**, so the rest of the pipeline can be demonstrated end to end. Connecting it to the Claude API for real invoice reading from photos and PDFs is the next step, and only `extract.py` needs to change.

## Tech stack

| Part | Tool |
|---|---|
| Language | Python |
| Web app / UI | Streamlit |
| Database | SQLite |
| Data handling | pandas |
| Charts | Plotly |
| AI invoice reading (planned) | Claude API (Anthropic) |

## Project structure

```
app.py            The web app: pages, layout and charts
extract.py        Invoice reading (sample data for now, Claude API next)
database.py       SQLite storage: invoices, inventory, payments, GST
requirements.txt  Python packages
.gitignore        Keeps secrets and local files out of Git
```

## Run it locally (Windows)

1. Install Python 3.10 or newer and Git.
2. Clone the repo and open the folder:
   ```
   git clone https://github.com/[username]/[repo-name].git
   cd [repo-name]
   ```
3. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install the packages:
   ```
   pip install -r requirements.txt
   ```
5. Start the app:
   ```
   streamlit run app.py
   ```
   It opens in your browser at `http://localhost:8501`.

On Mac or Linux, activate the environment with `source venv/bin/activate`.

## Roadmap

- Real invoice extraction with Claude vision (photos, PDFs, messy scans)
- Separate CGST/SGST and IGST based on supplier state
- WhatsApp invoice upload
- Hindi and regional-language invoices
- Login and per-business data separation
- GST return export
- Move from Streamlit and SQLite to React, FastAPI and PostgreSQL for production

## Notes

- Sample data only. No real customer or GST details are used in this repo.
- The database file (`karobar.db`) is created automatically on first run and is not stored in Git.
