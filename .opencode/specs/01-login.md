---
# Spec: Login

## Overview
This feature implements user authentication with login, logout, and session management using JWT tokens. It provides the foundational security layer for the personal finance tracker, allowing users to securely access their expense data.

## Depends on
None - this is the first feature in the roadmap.

## Routes
- `GET /` — Landing page with login/register form — public
- `POST /auth/login` — Authenticate user and create session — public
- `POST /auth/logout` — End session and clear cookie — logged-in
- `GET /dashboard` — Main expense tracker page — logged-in
- `POST /add` — Add new expense — logged-in
- `POST /remove` — Remove selected expenses — logged-in

## Database changes
No database changes required. The `users` table already exists in `Database/db.py` with the required schema (id, name, email, password_hash, created_at).

## Templates
- **Create:** No new templates needed
- **Modify:**
  - `templates/index.html` — Add session validation to redirect to landing if not authenticated
  - `templates/landing.html` — Ensure login form posts to `/auth/login`, register to `/auth/register`

## Files to change
- `app.py` — Create new Flask application with all routes

## Files to create
- None

## New dependencies
No new dependencies. All required packages (`flask`, `python-jose[cryptography]`, `passlib[bcrypt]`, `werkzeug`) are already in `pyproject.toml`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (bcrypt via passlib)
- Use CSS variables — never hardcode hex values
- All templates extend `index.html` base template pattern
- JWT tokens stored in httpOnly cookies
- Session validation middleware for protected routes

## Definition of done
- [ ] Running `python app.py` starts Flask server on port 5000
- [ ] GET `/` renders landing.html with login/register forms
- [ ] POST `/auth/login` with valid credentials redirects to `/dashboard`
- [ ] POST `/auth/login` with invalid credentials shows error on landing page
- [ ] POST `/auth/register` creates new user and redirects to dashboard
- [ ] POST `/auth/logout` clears session and redirects to landing
- [ ] GET `/dashboard` without session redirects to `/`
- [ ] GET `/dashboard` with valid session shows expense tracker
- [ ] POST `/add` adds expense for logged-in user
- [ ] POST `/remove` removes selected expenses for logged-in user