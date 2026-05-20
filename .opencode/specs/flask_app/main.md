# Flask App Plan

---

## 1. Overview

Add database initialization and authentication to `test.py` using existing `Database/` modules.

Reuse:
- `Database/db.py` — expense db (init, seed, get_db, CATEGORIES)
- `Database/auth.py` — token/password/user helpers
- `Database/config.py` — env var loading

---

## 2. Files to Change

| File | Action |
|---|---|
| `test.py` | Add db init, auth routes, session handling |
| `.env` | Add `USER_DATABASE_NAME` (optional, for future) |

---

## 3. test.py Changes

### 3.1 Imports

```python
from Database.db import init_db, seed_db, get_db, CATEGORIES
from Database.auth import (
    verify_password, create_token, decode_token,
    create_user, get_user_by_email, get_user_by_id,
    hash_password,
)
```

### 3.2 Startup Init (before app creation)

```python
init_db()
seed_db()
```

### 3.3 Session Config

```python
STANDARD_EXPIRE = 86400
REMEMBER_ME_EXPIRE = 604800
```

### 3.4 Routes

| Route | Method | Auth | Description |
|---|---|---|---|
| `/auth/login` | POST | No | Verify email+password, set session cookie, redirect `/dashboard` |
| `/auth/register` | POST | No | Create user, set session cookie, redirect `/dashboard` |
| `/auth/logout` | POST | No | Clear session cookie, redirect `/landing` |
| `/dashboard` | GET | Yes | Serve dashboard page |
| `/get-user` | GET | Yes | Return current user info as JSON |

### 3.5 Auth Logic

- Read session from cookie → decode token → get `user_id`
- On invalid/missing session → redirect to `/landing?error=...`
- On success → serve dashboard with user-specific data

### 3.6 Session Cookie

- `httponly=True`, `samesite="lax"`, `secure` (True in production)
- Reuse token functions from `Database/auth.py`

---

## 4. .env Changes

```env
USER_DATABASE_NAME=Database/user.db
```

---

## 5. Execution Order

1. Update imports in `test.py`
2. Call `init_db()` and `seed_db()` before app creation
3. Add auth routes (`/auth/login`, `/auth/register`, `/auth/logout`)
4. Add protected routes (`/dashboard`, `/get-user`)
5. Update `.env` with optional `USER_DATABASE_NAME`