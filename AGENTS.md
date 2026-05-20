# Agent Instructions

## Database

- Database config: `Database/config.py` (`DATABASE_NAME` from env, defaults to `expense_tracker.db`)
- Always use `get_db()` from `Database/db.py` - never hardcode the database filename
- `get_db()` enables foreign keys: `conn.execute("PRAGMA foreign_keys = ON")`
- Use parameterized queries only (no string formatting in SQL)

## Scripts

- `seed_expenses.py <user_id> <count> <months>` - insert test expenses
- `generate_user.py <count>` - create test users

## Testing

- Test file: `test.py` (matches `python_files` in pyproject.toml)
- Run: `python test.py`
- No pytest config beyond testpaths; no lint/typecheck tools configured

## Stack

- Flask + FastAPI (both in requirements)
- Jinja2 for templates
- SQLite with `werkzeug.security` for password hashing
- Virtual environment at `.venv/`