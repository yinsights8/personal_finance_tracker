# Agent Instructions

## Stack
- **Flask** only (FastAPI is in pyproject.toml but unused in code)
- Jinja2 templates, Chart.js for dashboard charts (CDN-loaded)
- SQLite via `sqlite3` stdlib, Pydantic schemas in `Schemas/` (unused by Flask routes)
- JWT auth via `python-jose` + bcrypt via `passlib[bcrypt]`

## Database
- Config: `Database/config.py` (`DATABASE_NAME` from env, defaults to `expense_tracker.db`)
- **Always use `get_db()` from `Database/db.py`** — never hardcode filename
- `get_db()` enables foreign keys: `PRAGMA foreign_keys = ON`
- Use parameterized queries only (no string formatting in SQL)
- DB init: `init_db()` in `Database/db.py` creates `users` + `expenses` tables
- Seeded demo user: `demo@spendly.com` / `demo123` (autocreated by `seed_db()`)

## Running
- **Start**: `python app.py` (Flask dev server on `0.0.0.0:5000`)
- **Test/development server**: `python test.py` (also Flask, port 5000)
- Activate venv: `.venv\Scripts\activate` (Windows)

## Testing
- No pytest — test file is `test.py` (standalone Flask app with full routes)
- Run: `python test.py`

## Auth
- Password rules: 8-72 chars, 1+ letter, 1+ digit, 1+ special char
- Session: JWT in `httpOnly` cookie named `session`, 24h expiry by default
- Auth helper: `require_auth` decorator in `app.py:25` redirects to `/landing`

## Routes (app.py)
| Route | Method | Auth | Purpose |
|---|---|---|---|
| `/` | GET | No | Redirects to `/landing` |
| `/landing` | GET | No | Login/register page |
| `/auth/login` | POST | No | Email+password, sets session cookie |
| `/auth/register` | POST | No | Creates user, sets session cookie |
| `/auth/logout` | POST | No | Clears session cookie |
| `/dashboard` | GET | Yes | Expense tracker with Chart.js analytics |
| `/profile` | GET | Yes | User summary, stats, recent transactions |
| `/add` | POST | Yes | Add expense |
| `/remove` | POST | Yes | Delete selected expenses |
| `/api/chart-data` | GET | Yes | JSON: category/weekly/monthly/yearly breakdown |

## Categories
`["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]`

## Conventions
- No lint/formatter config (no CI, no pre-commit hooks)
- No generated code or build step — run `python test.py` first to create demo user, then browse
- Templates use Bootstrap 5.3 (CDN)
