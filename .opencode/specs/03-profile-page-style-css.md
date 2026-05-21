# Spec: Profile Page Style CSS

## Overview
This feature adds dedicated CSS styling and a complementary JavaScript file to the profile page, matching the visual design language of the landing page. The profile page currently extends `index.html` and inherits only Bootstrap's base styling. This step introduces a custom `style_profile.css` with card-based sections, avatar circle, stats grid, category badges with progress bars, and a `main_profile.js` for password validation on the change-password form — all using CSS variables to avoid hardcoded hex values.

## Depends on
- Step 03 — Profile Page Design (the `/profile` route and `templates/profile.html` must exist)

## Routes
No new routes.

## Database changes
No database changes.

## Templates
- **Modify:** `templates/profile.html` — apply custom CSS classes from `style_profile.css`, add `{% block extra_css %}` and `{% block scripts %}` references

## Files to change
- `templates/profile.html` — replace raw Bootstrap classes with styled CSS component classes

## Files to create
- `static/style_profile.css` — full styling for the profile page using CSS variables
- `static/main_profile.js` — password strength validation for the change-password form

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `index.html`
- No inline styles — all styling via CSS classes

## Definition of done
- [ ] `GET /profile` renders with card-based sections matching landing page aesthetic
- [ ] User info card shows avatar circle with first initial, name, email, member-since date
- [ ] Summary stats row shows total spent, transaction count, and top category in card-style stat boxes
- [ ] Recent transactions table has styled category badges per category
- [ ] Category breakdown section shows progress bars for each category
- [ ] Change-password form has live password validation via `main_profile.js`
- [ ] No inline `style` attributes in `profile.html`
- [ ] No hardcoded hex colour values — all colors via `var(--...)`
