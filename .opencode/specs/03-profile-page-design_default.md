# Spec: Profile Page Design

## Overview
Adds a profile page where logged-in users can view their account details (name, email, member-since date) and update their name, email, or password. This builds on the existing auth system to give users control over their account settings.

## Depends on
- Step 01 — Login (users table, session management)
- Step 02 — Login and Logout (auth routes, JWT cookies)

## Routes
- `GET /profile` — Display profile form with user info — logged-in
- `POST /profile/update` — Update name and/or email — logged-in
- `POST /profile/change-password` — Change password — logged-in

## Database changes
No database changes. The existing `users` table already has `id, name, email, password_hash, created_at`.

## Templates
- **Create:** `templates/profile.html`
- **Modify:** `templates/index.html` — add "Profile" link in navbar

## Files to change
- `app.py` — add 3 new routes
- `templates/index.html` — add navbar link to /profile
- `static/style_profile.css` - add a style specific to /profile page or create new if already exists and match the font and style from the landing page. 
- `static/main_profile.js` - create new specific to /profile page if already exists and match the font and style from the landing page.

## Files to create
- `templates/profile.html`
- `static/style_profile.css`
- `static/main_profile.js`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (bcrypt via passlib)
- Use CSS variables — never hardcode hex values
- All templates extend `index.html`

## Definition of done
- [ ] `GET /profile` renders profile page with user name, email, and member-since date
- [ ] `POST /profile/update` saves new name/email and redirects back to /profile with a success message
- [ ] `POST /profile/change-password` validates old password, updates to new password, redirects with success/error
- [ ] Navbar on dashboard includes a "Profile" link
- [ ] Visiting `/profile` without a session redirects to `/landing`
