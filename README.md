# 📘 Django Portfolio Manager & Accounting System

A complete portfolio and accounting management system built with **Django**, designed for multi-partner companies with:
- 💹 Investment Tracking
- 💼 Double Entry Bookkeeping
- 📊 Financial Reports (Trial Balance, P&L, Balance Sheet)
- 🧾 Journal Management (with auto-generated serials)
- 👥 Shareholder Capital Ledger

---

## 🚀 Features

- ✅ **Portfolio Management** — Track investments with units, symbols, face value, and cost
- ✅ **Double Entry Bookkeeping** — Journalized transactions with debit/credit entries
- ✅ **Journal Types** — Auto-categorized journals (Investment, Cash, Bank, General)
- ✅ **Auto Serial Numbers** — For each journal type (`INV-0001`, `CASH-0001`, etc.)
- ✅ **Day Journal** — View all entries for a selected date
- ✅ **Financial Reports**
  - Trial Balance (by account type, with date filters)
  - Profit & Loss (planned)
  - Balance Sheet (planned)
- ✅ **Shareholders Module** — Track capital contributions and link to chart of accounts

---

## 📁 Project Structure

django-portfolio/ ├── core/ │ ├── models.py │ ├── views.py │ ├── forms.py │ ├── utils.py │ ├── urls.py │ └── templates/ │ ├── base.html │ ├── reports/ │ │ └── day_journal.html │ ├── journals/ │ │ ├── list.html │ │ ├── edit.html │ │ └── delete_confirm.html │ └── transactions/add_transaction.html ├── manage.py ├── db.sqlite3 ├── README.md └── requirements.txt


---

## ⚙️ Installation Guide

```bash
git clone https://github.com/YOUR_USERNAME/django-portfolio-manager.git
cd django-portfolio-manager

# Set up virtual environment
python -m venv env
env\Scripts\activate  # or source env/bin/activate on Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run the development server
python manage.py runserver
