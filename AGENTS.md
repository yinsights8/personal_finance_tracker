# Agent Instructions

## Database
- Database config: `Database/config.py` (`DATABASE_NAME` from env, defaults to `expense_tracker.db`)
- Always use `get_db()` from `Database/db.py` - never hardcode the database filename
- `get_db()` enables foreign keys: `conn.execute("PRAGMA foreign_keys = ON")`
- Use parameterized queries only (no string formatting in SQL)

## Testing
- Test file: `test.py` (matches `python_files` in pyproject.toml)
- Run: `python test.py`

## Stack
- Flask + FastAPI (both in requirements)
- Jinja2 for templates
- SQLite with `werkzeug.security` for password hashing
- JWT auth in `Database/auth.py`
- Virtual environment at `.venv/`

## Key Files
- `app.py` - Flask routes (create if not exists)
- `Database/auth.py` - JWT tokens, password hashing (bcrypt)
- `Database/db.py` - Database connection and init
- `templates/landing.html` - Login/register page
- `templates/index.html` - Main expense tracker dashboard

## Scripts
- `seed_expenses.py <user_id> <count> <months>` - Insert test expenses
- `generate_user.py <count>` - Create test users