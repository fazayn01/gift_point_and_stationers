# Gift Point & Stationers — Inventory Management System

I built a basic inventory system for a small stationery and gift shop called Gift Point & Stationers. The backend is a Flask REST API connected to an SQLite database, and the frontend is plain HTML, CSS and JavaScript that talks to the API using fetch() calls.

---

## What the system does

The system handles the core operations of a small shop:

- Staff can log in with a role (admin, employee, or owner) and each role gets a different view
- Admin can add, edit, delete and search products
- Employee can process sales through a cart checkout and link customers for loyalty points
- Owner can view sales reports and revenue summaries
- Live currency conversion is shown using an external exchange rate API

CRUD is fully implemented for Products and Customers. Orders are created through the checkout flow.

---

## Project files

```
gift_point_and_stationers/
├── app.py           - Flask backend, all API routes
├── database.py      - SQLite setup and seed data
├── test_app.py      - Unit and integration tests
├── requirements.txt - Python dependencies
├── index.html       - Frontend page
├── style.css        - Styling
├── app.js           - Frontend logic and API calls
└── inventory.db     - Auto-created on first run
```

---

## How to run it

**Requirements:** 
Python 3.9 or above, pip, any browser

**Step 1 — Clone the repo**
```bash
git clone https://github.com/fazayn01/gift_point_and_stationers.git
cd gift_point_and_stationers
```

**Step 2 — Create a virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Mac/Linux
source .venv/bin/activate
```

**Step 3 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 4 — Start the server**
```bash
python app.py
```

The database is created and seeded automatically on first run. Open your browser and go to http://136.113.130.72:3000

---

## Login credentials (seeded)

| Role     | User ID | Name  | Password   |
| -------- | ------- | ----- | ---------- |
| Admin    | 1       | Admin | admin123   |
| Employee | 241462  | Aruj  | aruj123    |
| Owner    | 3       | Owner | owner123   |

---

## Running the tests

```bash
python -m unittest test_app.py -v
```

There are 9 tests in total — 8 unit tests covering login, product CRUD and customer operations, and 1 integration test that runs a full checkout and checks that stock, loyalty points and order records all update correctly.

---

## Issues I ran into and fixed

**1. Server crash on duplicate phone number**
When I tried to register a customer with a phone number that already existed, the server crashed with `NameError: name 'sqlite3' is not defined`. The issue was that I was catching `sqlite3.IntegrityError` but had never imported the sqlite3 module at the top of app.py. Fixed by adding `import sqlite3`.

Reference: https://chatgpt.com/share/6a58d953-06b8-83ee-9639-0c89c0942050

**2. Database file being created in the wrong folder**
The DB_PATH was using `dirname(dirname(__file__))` which put inventory.db one level above the project folder. Changed it to use `dirname(abspath(__file__))` so it always creates the database in the project folder.

**3. Database not initialising on startup**
Running `python app.py` on a fresh clone gave a `no such table: Product` error because init_db() was never being called. Added the call at the top of app.py so the tables are always created before the first request.

---

## References

- Flask documentation: https://flask.palletsprojects.com
- Flask-CORS: https://flask-cors.readthedocs.io
- Fetch API (MDN): https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- CSS Flexbox (W3Schools): https://www.w3schools.com/css/css3_flexbox.asp
- Live exchange rates: https://open.er-api.com
- Database setup help: https://chatgpt.com/share/6a58d918-09b0-83e8-87cc-12abbefc856b
- Backend API help: https://chatgpt.com/share/6a58d92a-ee94-83e8-9203-ff3e48c4b696
- Exchange rate proxy: https://chatgpt.com/share/6a58d940-9248-83ee-88f6-52af9d1dc0ca
- sqlite3 import fix: https://chatgpt.com/share/6a58d953-06b8-83ee-9639-0c89c0942050
- Checkout and invoice: https://chatgpt.com/share/6a58d960-7070-83ee-8c07-6aada24c5c5b
