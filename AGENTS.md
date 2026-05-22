# Agent Instructions

## Stack
- **Flask** only
- Jinja2 templates, Chart.js for dashboard charts (CDN-loaded)
- SQLite via `sqlite3` stdlib
- JWT auth via `python-jose` + bcrypt via `passlib[bcrypt]`

## Database
- Config: `src/shared/config.py` (`DATABASE_NAME` from env, defaults to `expense_tracker.db`)
- **Always use `get_db()` from `src/shared/db.py`** — never hardcode filename
- `get_db()` enables foreign keys: `PRAGMA foreign_keys = ON`
- Use parameterized queries only (no string formatting in SQL)
- DB init: `init_db()` in `src/shared/db.py` creates `users` + `expenses` tables
- Seeded demo user: `demo@spendly.com` / `demo123` (autocreated by `seed_db()`)

## Running
- **Start**: `python src/app.py` (Flask dev server on `0.0.0.0:5000`)
- **Test/development server**: `python tests/test_app.py` (also Flask, port 5000)
- Activate venv: `.venv\Scripts\activate` (Windows)

## Testing
- No pytest — test file is `tests/test_app.py` (standalone Flask app with full routes)
- Run: `python tests/test_app.py`

## Auth
- Password rules: 8-72 chars, 1+ letter, 1+ digit, 1+ special char
- Session: JWT in `httpOnly` cookie named `session`, 24h expiry by default
- Auth helper: `require_auth` decorator in `src/features/auth/routes.py` redirects to `/`

## Routes (organized by feature)

| Route | Method | Auth | Purpose | File |
|---|---|---|---|---|
| `/` | GET | No | Redirects to `/landing` | `src/features/auth/routes.py` |
| `/landing` | GET | No | Login/register page | `src/features/auth/routes.py` |
| `/auth/login` | POST | No | Email+password, sets session cookie | `src/features/auth/routes.py` |
| `/auth/register` | POST | No | Creates user, sets session cookie | `src/features/auth/routes.py` |
| `/auth/logout` | POST | No | Clears session cookie | `src/features/auth/routes.py` |
| `/dashboard` | GET | Yes | Expense tracker with Chart.js analytics | `src/features/expenses/routes.py` |
| `/profile` | GET | Yes | User summary, stats, recent transactions | `src/features/profile/routes.py` |
| `/add` | POST | Yes | Add expense | `src/features/expenses/routes.py` |
| `/remove` | POST | Yes | Delete selected expenses | `src/features/expenses/routes.py` |
| `/api/chart-data` | GET | Yes | JSON: category/weekly/monthly/yearly breakdown | `src/features/expenses/routes.py` |

## Categories
`["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]`

## Conventions
- No lint/formatter config (no CI, no pre-commit hooks)
- No generated code or build step — run `python tests/test_app.py` first to create demo user, then browse
- Templates use Bootstrap 5.3 (CDN)
