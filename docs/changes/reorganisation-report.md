# Project Reorganisation Report

## 1. Motivation

The original codebase had several structural issues:

- **Duplicated app logic**: `app.py` (333 lines) and `test.py` (256 lines) shared ~80% duplicate route code with slight differences in auth patterns and validation
- **Dead code**: `Schemas/` directory contained Pydantic models never imported by any route
- **Mixed concerns**: `Database/` bundled DB connection, config, auth, and seeding together
- **Flat layout**: Python modules at root level mixed with scripts, docs, and config
- **Unused dependencies**: `fastapi`, `uvicorn`, and `pydantic` in `pyproject.toml` but never used in code
- **Broken demo login**: `seed_db()` used werkzeug's pbkdf2 hash, but login verification used bcrypt — seeded demo user could never log in

---

## 2. Before vs. After

### Before

```
personal_finance_tracker/
├── app.py                    # 333 lines — all routes + auth helpers
├── test.py                   # 256 lines — duplicate routes
├── Database/
│   ├── db.py                 # DB connection, init, seeding
│   ├── auth.py               # JWT, password hashing, user CRUD
│   └── config.py             # Env config
├── Schemas/                  # ✗ DEAD CODE — Pydantic models, unused
│   ├── category.py
│   ├── expense.py
│   └── user.py
├── templates/                # Flat — 3 templates
├── static/                   # Flat — 4 static files
├── plans/                    # Docs mixed at root
├── implimented_plans/
└── backup/
```

### After

```
src/                          # All application source code
├── app.py                    # Flask entry point (merged from app.py + test.py)
├── features/                 # Feature-based modules
│   ├── auth/
│   │   ├── routes.py         # login, register, logout, landing
│   │   └── service.py        # JWT, bcrypt, user CRUD
│   ├── expenses/
│   │   └── routes.py         # dashboard, add, remove, chart-data
│   └── profile/
│       └── routes.py         # profile page
├── shared/                   # Cross-cutting concerns
│   ├── db.py                 # get_db(), init_db(), seed_db()
│   └── config.py             # DATABASE_NAME, DEBUG
├── templates/                # Jinja2 templates
│   ├── landing.html
│   ├── index.html
│   └── profile.html
└── static/
    ├── css/
    │   ├── dashboard.css
    │   └── profile.css
    └── js/
        ├── dashboard.js
        └── profile.js
tests/
├── __init__.py
└── test_app.py               # Standalone test/development server
docs/
├── plans/                    # Migrated from root plans/
├── implemented_plans/        # Migrated from root implimented_plans/
└── backup/
    └── backup-plan.md        # Migrated from root backup/
```

---

## 3. Key Changes

| Change | Details |
|--------|---------|
| **Feature-based structure** | Code grouped by feature (auth, expenses, profile) instead of by layer |
| **Merged app.py + test.py** | `src/app.py` now uses Flask Blueprints; `tests/test_app.py` is a standalone test server |
| **Database/ → src/shared/** | `db.py` and `config.py` moved to `src/shared/` |
| **Database/auth.py → src/features/auth/service.py** | Auth logic now lives in the auth feature |
| **Removed Schemas/** | Dead Pydantic models deleted (never used by routes) |
| **Templates → src/templates/** | All 3 templates moved with updated static references |
| **Static files reorganised** | `static/{css,js}/` with feature-appropriate names (`dashboard.css`, `profile.js`, etc.) |
| **docs/ directory** | Plans, implemented plans, and backup docs consolidated under `docs/` |
| **pyproject.toml cleaned** | Removed `fastapi`, `uvicorn`, `pydantic` deps; added `pythonpath = ["src"]` |

---

## 4. Bugs Fixed

### 4.1. Demo login broken (password hash mismatch)

**Symptom**: Seeded demo user `demo@spendly.com` / `demo123` could never log in.

**Root cause**: `seed_db()` in `Database/db.py` used `werkzeug.security.generate_password_hash("demo123")` (pbkdf2), but login verification in `Database/auth.py` used `bcrypt.checkpw()`. These algorithms are incompatible.

**Fix**: `src/shared/db.py:55` now imports and uses `hash_password()` from `src/features/auth/service.py` (bcrypt).

```python
# Before (broken)
from werkzeug.security import generate_password_hash
cursor.execute("INSERT INTO users ... VALUES (?, ?, ?)",
    ("Demo User", "demo@spendly.com", generate_password_hash("demo123")))

# After (fixed)
from features.auth.service import hash_password
cursor.execute("INSERT INTO users ... VALUES (?, ?, ?)",
    ("Demo User", "demo@spendly.com", hash_password("demo123")))
```

### 4.2. Profile page rendering without base layout

**Symptom**: Profile page lacked DOCTYPE, `<html>`, `<body>`, and navbar.

**Root cause**: `profile.html` had no `{% extends "index.html" %}`, so Jinja2 rendered only the block content without the base template layout.

**Fix**: Added `{% extends "index.html" %}` as the first line of `src/templates/profile.html`.

---

## 5. Running the App

```bash
# Production server
python src/app.py

# Test/development server (with seeded data)
python tests/test_app.py
```

Both start on `http://0.0.0.0:5000`.

---

## 6. All Routes

| Route | Method | Auth | File |
|-------|--------|------|------|
| `/` | GET | No | `src/features/auth/routes.py` |
| `/landing` | GET | No | `src/features/auth/routes.py` |
| `/auth/login` | POST | No | `src/features/auth/routes.py` |
| `/auth/register` | POST | No | `src/features/auth/routes.py` |
| `/auth/logout` | POST | No | `src/features/auth/routes.py` |
| `/dashboard` | GET | Yes | `src/features/expenses/routes.py` |
| `/profile` | GET | Yes | `src/features/profile/routes.py` |
| `/add` | POST | Yes | `src/features/expenses/routes.py` |
| `/remove` | POST | Yes | `src/features/expenses/routes.py` |
| `/api/chart-data` | GET | Yes | `src/features/expenses/routes.py` |
| `/get-user` | GET | Yes | `tests/test_app.py` (test server only) |

---

## 7. Verification

All routes tested with live HTTP requests:

```
✅ Landing page     — 200
✅ Login flow       — 302 → 200 with session cookie
✅ Dashboard        — 200 (analytics, charts, table, KPIs all render)
✅ Profile          — 200 (proper DOCTYPE, navbar, stats, chart)
✅ Add expense      — 302 → 200
✅ Logout           — 302 → 200
✅ Static files     — /static/css/dashboard.css, /static/js/profile.js, etc. all 200
✅ Chart API        — /api/chart-data returns JSON 200
```
