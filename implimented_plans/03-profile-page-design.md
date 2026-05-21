# Implementation Plan: Profile Page Design (Step 03)

## Changes

### 1. Clean up `Database/auth.py`
- Remove `update_user()` and `update_password()` (unused)

### 2. Delete unused static files
- `static/style_profile.css`
- `static/main_profile.js`

### 3. Tidy `templates/index.html`
- Remove `{% block extra_css %}` from `<head>`
- Show `{{ user.name }}` in navbar for "logged-in state" in DoD
- Keep "Profile" nav link

### 4. Rewrite `app.py`
- Remove `POST /profile/update` and `POST /profile/change-password`
- Rewrite `GET /profile` to query DB for:
  - `user`, `total_spent`, `transaction_count`, `top_category`
  - `recent_transactions` (last 5), `category_totals` per category
- Auth guard: `require_auth` redirects to `/landing`

### 5. Rewrite `templates/profile.html`
- Extends `index.html`
- Zero inline styles — all CSS classes
- Use CSS variables — no hex values
- Four sections:
  1. User info card — avatar initials, name, email, member-since
  2. Summary stats — total spent, transaction count, top category
  3. Transaction history table — date, description, category badge, amount
  4. Category breakdown — per-category totals with progress bars

### 6. Add CSS classes to `static/style.css`
- `.avatar-initials`, `.stats-row`, `.stat-item`, `.stat-value`, `.stat-label`
- `.category-badge`, `.badge-{category}` for each category
- `.category-row`, `.progress-fill`, `.breakdown-table`
- All colors via `var(--...)` in `:root`

## Key Decisions
- Redirect to `/landing` (not `/login` — landing page IS the login page)
- Use `require_auth` decorator for auth guard
- No new static files — everything in existing `style.css`
- DB queries from `app.py` — no hardcoded data
