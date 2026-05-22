# App Route Plan - Personal Finance Tracker

## Overview

Add FastAPI backend with Jinja2 templates and JWT cookie-based authentication to serve the existing frontend.
> **Note**: Earned/Spent feature is NOT included. Only existing database fields are used.

---

## Dependencies

Add to `pyproject.toml`:
```
fastapi
uvicorn[standard]
jinja2
python-multipart
python-jose[cryptography]
passlib[bcrypt]
```

---

## Existing Database Fields (No Changes)

**`expenses` table** (from `Database/db.py`):
- `id` INTEGER PRIMARY KEY
- `user_id` INTEGER (FK to users)
- `amount` REAL NOT NULL
- `category` TEXT NOT NULL
- `date` TEXT NOT NULL
- `description` TEXT (optional)
- `created_at` TEXT

**`users` table** (from `Database/db.py`):
- `id` INTEGER PRIMARY KEY
- `name` TEXT NOT NULL
- `email` TEXT UNIQUE NOT NULL
- `password_hash` TEXT NOT NULL
- `created_at` TEXT

### Template ↔ DB Mapping

| Template Field | DB Column | Notes |
|----------------|-----------|-------|
| Category dropdown | `category` | Food, Transport, Bills, Health, Entertainment, Shopping, Other |
| Price input | `amount` | Number field, min=0 |
| Description input | `description` | Optional, placeholder: "enter your description" |
| Date | `date` | Auto-captured or user-provided |
| *(commented)* | `quantity` | Not used |
| *(commented)* | `name` | Not used |

---

## Route Endpoints

### Auth Routes
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/auth/login` | Render login.html |
| POST | `/auth/login` | Verify credentials, set JWT cookie, redirect `/` |
| GET | `/auth/register` | Render register.html |
| POST | `/auth/register` | Create user with hashed password, redirect `/auth/login` |
| POST | `/auth/logout` | Clear session cookie, redirect `/auth/login` |

### App Routes (Protected)
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Dashboard - render index.html with filtered expenses |
| POST | `/add` | Add expense/income, redirect `/` |
| POST | `/remove` | Delete selected expenses, redirect `/` |

### Static Files
| Path | File |
|------|------|
| `/static/style.css` | static/style.css |
| `/static/main.js` | static/main.js |

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `pyproject.toml` | Modify | Add 6 dependencies |
| `.env` | Modify | Add `SECRET_KEY=your-secret-key` |
| `Database/auth.py` | Create | `hash_password()`, `verify_password()`, `create_token()`, `decode_token()` |
| `main.py` | Create | FastAPI app with all routes + templates |
| `templates/index.html` | Modify | Category dropdown, add description, comment out quantity |
| `templates/login.html` | Create | Login form |
| `templates/register.html` | Create | Registration form |

---

## Authentication

### JWT Cookie
- Name: `session`
- Type: `httpOnly`, `secure=False` (dev), `samesite="lax"`
- Payload: `{user_id: int, exp: datetime}`

### Auth Module (`Database/auth.py`)
```python
def hash_password(password: str) -> str
def verify_password(plain: str, hashed: str) -> bool
def create_token(user_id: int, secret_key: str) -> str
def decode_token(token: str, secret_key: str) -> dict | None
```

### Protected Route Dependency
```python
def get_current_user(session: str | None = Cookie(None)) -> int
# Returns user_id or raises HTTPException 401
```

---

## Error Handling & Exceptions

### Exception Types

| Exception | HTTP Code | Cause | Response |
|-----------|-----------|-------|----------|
| `UnauthorizedException` | 401 | Invalid/missing session | Redirect to `/auth/login` |
| `ForbiddenException` | 403 | User not authorized for resource | 403 Forbidden page |
| `NotFoundException` | 404 | Resource not found | 404 Not Found page |
| `ValidationException` | 422 | Invalid form data | Re-render form with errors |
| `DatabaseException` | 500 | DB connection/error | 500 Internal Server Error |
| `ConflictException` | 409 | Email already exists | Re-render register with error |

### Error Handling Strategy

1. **Auth Errors**: Redirect to login page with error message
2. **Validation Errors**: Re-render form with inline error messages
3. **Database Errors**: Log error, show 500 page
4. **404 Errors**: Custom 404 template

### Try/Catch Blocks

| Operation | Error Handling |
|-----------|----------------|
| DB Connection | `try/except sqlite3.Error` → show 500 error |
| User Lookup | `try/except` → return None if not found |
| Password Verify | `try/except` → return False on error |
| Form Parsing | Pydantic validation → return 422 with details |
| JWT Decode | `try/except` → return None, clear cookie |

---

## Validation Rules

### Form Input Rules

| Field | Type | Constraints | Error Message |
|-------|------|-------------|---------------|
| Category | Select | Required, must be in CATEGORIES list | "Please select a valid category" |
| Amount | Number | Required, > 0, max 999999.99 | "Amount must be greater than 0" |
| Description | Text | Optional, max 500 chars | "Description too long" |

### Auth Rules

| Field | Rules | Error Message |
|-------|-------|---------------|
| Name | Required, 2-100 chars | "Name must be 2-100 characters" |
| Email | Required, valid email format, unique | "Email already registered" |
| Password | Required, min 8 chars | "Password must be at least 8 characters" |
| Confirm Password | Must match password | "Passwords do not match" |

### Security Rules

1. **Password Storage**: Hash with `passlib` + `bcrypt`, never store plain text
2. **Session Expiry**: JWT expires in 24 hours
3. **CSRF Protection**: SameSite cookies + form tokens
4. **Input Sanitization**: Escape all user input in templates
5. **SQL Injection**: Use parameterized queries only

---

## Template Changes

### `templates/index.html`

**Changes:**
1. Replace "Item" label → "Category"
2. Replace text input → `<select name="name">` with options:
   - Food, Transport, Bills, Health, Entertainment, Shopping, Other
3. Add description input group after price:
   ```html
   <div class="input-group mb-3">
       <span class="input-group-text">Description</span>
       <input type="text" class="form-control" name="description"
              placeholder="enter your description" autocomplete="off">
   </div>
   ```
4. Comment out quantity input group (lines 61-76)
5. Table header "Item" → "Category"
6. Remove Earned/Spent radios
7. All form fields disabled when `{{disable_button}}` is true

---

## Template Files

### `templates/login.html`
- Email input (`type="email"`, name="email")
- Password input (`type="password"`, name="password")
- Submit button
- Link to `/auth/register`
- Error message display area

### `templates/register.html`
- Name input (`type="text"`, name="name")
- Email input (`type="email"`, name="email")
- Password input (`type="password"`, name="password")
- Confirm password (`type="password"`, name="confirm_password")
- Submit button
- Link to `/auth/login`
- Error message display area

### Error Templates
- `templates/404.html` - Not Found page
- `templates/500.html` - Internal Error page

---

## Dashboard Data Flow

1. `GET /` → `get_current_user()` validates session
2. Query expenses for `user_id` filtered by month/year (from query param `?month=YYYY-MM`)
3. Calculate total:
   - `total_expenses`: SUM(amount) for user
4. Pass to template: `data`, `total_expenses`, `month_year`, `categories`

---

## Implementation Order

1. Update `pyproject.toml` + install dependencies
2. Add `SECRET_KEY` to `.env`
3. Create `Database/auth.py`
4. Create `main.py`
5. Create `templates/login.html`
6. Create `templates/register.html`
7. Create `templates/404.html` and `templates/500.html`
8. Modify `templates/index.html`
9. when the user click on the url, it should direct to the landing page for login/register page.

---

## Notes

- Keep existing `expense_tracker.db` or recreate with migrations
- Run `init_db()` and `seed_db()` on first startup
- All routes except auth require valid session cookie
- Use parameterized queries for all DB operations