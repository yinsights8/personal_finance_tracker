# Personal Finance Tracker

A web-based expense tracking app built with **Flask**, **SQLite**, and **Chart.js**. Track spending across categories, visualize trends, and manage your finances from a clean dashboard.

## Features

- **Expense Dashboard** — Add, view, and delete expenses with real-time category breakdowns
- **Analytics** — Interactive Chart.js charts showing spending by category, week, month, and year
- **User Profiles** — Spending summary, top category, average/max/min stats, recent transactions
- **Authentication** — JWT-based login/register with bcrypt password hashing
- **Responsive UI** — Bootstrap 5.3 with dark theme

## Quick Start

```bash
# Clone and enter the project
git clone <repo-url>
cd personal_finance_tracker

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Start the development server
python app.py
```

The server runs on `http://0.0.0.0:5000`.

For a test/development server with seeded data:

```bash
python test.py
```

## Demo Account

| Email | Password |
|---|---|
| `demo@spendly.com` | `demo123` |

Created automatically when running `test.py` or `app.py` (first run only).

## Routes

| Route | Method | Auth | Description |
|---|---|---|---|
| `/` | GET | — | Redirects to landing |
| `/landing` | GET | — | Login / register page |
| `/auth/login` | POST | — | Sign in |
| `/auth/register` | POST | — | Create account |
| `/auth/logout` | POST | — | Sign out |
| `/dashboard` | GET | Yes | Expense tracker with charts |
| `/profile` | GET | Yes | User stats and transactions |
| `/add` | POST | Yes | Add an expense |
| `/remove` | POST | Yes | Delete expenses |
| `/api/chart-data` | GET | Yes | JSON chart data (category, weekly, monthly, yearly) |

## Expense Categories

`Food`, `Transport`, `Bills`, `Health`, `Entertainment`, `Shopping`, `Other`

## Tech Stack

- **Backend**: Flask, JWT (`python-jose`), bcrypt (`passlib`)
- **Frontend**: Jinja2 templates, Bootstrap 5.3, Chart.js
- **Database**: SQLite (stdlib `sqlite3`)

## Configuration

Environment variables (`.env`):

| Variable | Default | Description |
|---|---|---|
| `DATABASE_NAME` | `expense_tracker.db` | SQLite database file |
| `SECRET_KEY` | `default-secret-key-change-me` | JWT signing key |
| `DEBUG` | `True` | Flask debug mode |

## Project Structure

```
├── app.py              # Flask application (production)
├── test.py             # Flask application (development/testing)
├── Database/
│   ├── db.py           # Database connection, init, seeding
│   ├── auth.py         # JWT tokens, password hashing, user CRUD
│   └── config.py       # Configuration from environment
├── Schemas/            # Pydantic models (unused by routes)
├── templates/          # Jinja2 templates
│   ├── landing.html    # Login / register page
│   ├── index.html      # Dashboard with expense table & charts
│   └── profile.html    # User profile page
├── static/             # CSS and JS assets
└── .env                # Environment configuration
```
