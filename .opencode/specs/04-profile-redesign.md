# Profile Page — Feature Specification

**Project:** Personal Expense Tracker MCP  
**Document type:** UI Feature Spec  
**Version:** 1.0  
**Status:** Draft  

---

## 1. Overview

The Profile page is a user-facing settings and summary hub. It follows a two-column layout: a fixed left sidebar for identity and navigation, and a right panel split into a cover banner (top) and a scrollable content area (bottom). The design is based on the hand-sketched wireframe in `Scene_1.pdf`.

---

## 2. Layout Architecture

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌──────────────┬────────────────────────────────────┐  │
│  │              │         Cover Banner               │  │
│  │   Sidebar    │  (pink, editable, fixed height)    │  │
│  │  (purple)    ├────────────────────────────────────┤  │
│  │              │                                    │  │
│  │              │      Settings / Content Panel      │  │
│  │              │    (green, scrollable, dynamic)    │  │
│  │              │                                    │  │
│  └──────────────┴────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.1 Grid Definition

| Property | Value |
|---|---|
| Layout type | CSS Grid — 2 columns |
| Left column width | `260px` fixed |
| Right column width | `1fr` (fills remaining space) |
| Outer container | Full viewport height (`min-height: 100vh`) |
| Outer border | `2.5px solid` — accent blue (`#5BC8F0`) |
| Outer border radius | `18px` |
| Gap between columns | `0` (columns share a dividing border) |

### 2.2 Right Panel Split

The right column is a vertical flex column:

| Section | Height | Scroll |
|---|---|---|
| Cover Banner | `160px` fixed | No |
| Content Panel | `flex: 1` (fills rest) | `overflow-y: auto` |

---

## 3. Component Specifications

### 3.1 Left Sidebar

**Purpose:** Displays user identity, member info, and primary navigation.

**Styling:**

| Property | Value |
|---|---|
| Background | `#3d2e7c` (deep purple) |
| Padding | `28px 20px` |
| Position | `sticky`, `top: 0`, `height: 100vh` |
| Overflow | `overflow-y: auto` |
| Layout | Flex column |

#### 3.1.1 Avatar Section

Centred column stack: avatar circle → name → email → edit button.

| Element | Spec |
|---|---|
| Avatar circle | `72×72px`, `border-radius: 50%`, `background: rgba(255,255,255,0.2)` |
| Avatar content | First initial of `user.name`, `28px / 500 weight`, white |
| Border | `2px solid #5BC8F0` |
| User name | `14px / 500`, white, `text-align: center` |
| User email | `12px / 400`, `rgba(255,255,255,0.65)` |
| Edit button | Pill button — `11px`, `rgba(255,255,255,0.12)` background, `rgba(255,255,255,0.25)` border, `border-radius: 6px`, padding `2px 14px` |

#### 3.1.2 Divider

`1px solid rgba(255,255,255,0.2)`, margin `14px 0`.

#### 3.1.3 Member Since

`font-size: 11px`, colour `rgba(255,255,255,0.6)`. Rendered from `user.created_at[:10]`.

#### 3.1.4 Navigation Links

Two links, stacked vertically, `gap: 4px`:

| Link label | Icon prefix | Route |
|---|---|---|
| Account settings | `›` | `#account` |
| Dashboard settings | `›` | `#dashboard` |

**Nav item styling:**

| State | Style |
|---|---|
| Default | `color: rgba(255,255,255,0.8)`, transparent background, `border-radius: 8px`, padding `10px 12px` |
| Hover / Active | `background: rgba(255,255,255,0.15)`, `color: #fff` |

---

### 3.2 Cover Banner

**Purpose:** Decorative identity banner, editable by the user.

| Property | Value |
|---|---|
| Background | `#c2185b` (deep pink) or user-uploaded image |
| Height | `160px` fixed |
| Border bottom | `2.5px solid #5BC8F0` |
| Position | `relative` (to anchor the Edit button) |

**Edit button** (absolute, top-right):

| Property | Value |
|---|---|
| Position | `top: 14px`, `right: 16px` |
| Font | `12px`, white |
| Background | `rgba(0,0,0,0.25)` |
| Border | `1px solid rgba(255,255,255,0.4)` |
| Border radius | `6px` |
| Padding | `4px 14px` |
| Action | Opens cover image upload modal (future scope) |

> **Future scope:** Support user-uploaded cover image. Default state shows the solid colour with the Edit button.

---

### 3.3 Content Panel (Settings Load Page)

**Purpose:** Scrollable main content area. All data cards and settings forms live here.

| Property | Value |
|---|---|
| Background | `#4DB86A` (muted green) or inherits dark theme surface |
| Padding | `24px` |
| Overflow | `overflow-y: auto` |
| Layout | Flex column, `gap: 20px` |

Cards within this panel follow the existing `.profile-card` component style (dark surface, `border-radius`, consistent padding).

#### Sections rendered inside the Content Panel (in order):

| # | Section | Template condition | Content |
|---|---|---|---|
| 1 | Summary stats | Always | Total spent, transaction count, top category, avg/max/min per entry |
| 2 | Recent transactions | `{% if recent_transactions %}` | Table: Date, Description, Category badge, Amount |
| 3 | Category breakdown | `{% if category_totals %}` | Progress bars per category with amounts |
| 4 | Spending by category | Always | Horizontal bar chart (`profileCategoryBarChart`) |
| 5 | Category share | Always | Pie chart (`profileCategoryPieChart`) |
| 6 | Change password | Always | Password form with strength indicator |

---

## 4. Data & Template Variables

All variables are injected by the Flask route rendering `profile.html`.

| Variable | Type | Used in |
|---|---|---|
| `user.name` | string | Sidebar avatar initial, name label |
| `user.email` | string | Sidebar email label |
| `user.created_at` | string (ISO date) | Sidebar member since |
| `total_spent` | float | Summary — Total Spent |
| `transaction_count` | int | Summary — Transactions |
| `top_category` | string | Summary — Top Category |
| `avg_spent` | float | Summary — Avg per Entry |
| `max_spent` | float | Summary — Highest |
| `min_spent` | float | Summary — Lowest |
| `recent_transactions` | list[dict] | Transactions table (date, description, category, amount) |
| `category_totals` | dict[str, float] | Category breakdown bars + charts |
| `chart_data` | dict | JSON passed to Chart.js (contains `category_totals`) |

---

## 5. Chart Configuration

Both charts are rendered via **Chart.js** (loaded from CDN).

### 5.1 Category Bar Chart (`profileCategoryBarChart`)

| Property | Value |
|---|---|
| Type | `bar` (horizontal — `indexAxis: "y"`) |
| Colours | Per-category map (see Section 6) |
| Border radius | `6px` |
| Tooltip | `₹{value}` |
| X-axis ticks | `₹{value}` |
| Legend | Hidden |

### 5.2 Category Pie Chart (`profileCategoryPieChart`)

| Property | Value |
|---|---|
| Type | `pie` |
| Colours | Per-category map (see Section 6) |
| Legend | Position: `right` |
| Tooltip | `{label}: ₹{value} ({pct}%)` |
| Border width | `2px` |

---

## 6. Category Colour Map

| Category | Colour |
|---|---|
| Food | `#FF6384` |
| Transport | `#36A2EB` |
| Bills | `#FFCE56` |
| Health | `#4BC0C0` |
| Movie tickets | `#9966FF` |
| Shopping | `#FF9F40` |
| Other | `#C9CBCF` |

Category badges use `.cat-badge-{category}` CSS classes. Progress bar fills use `.progress-bar-{category.lower()}` classes.

---

## 7. Password Change Form

Located in the final card of the Content Panel.

| Field | Name attr | Type | Constraints |
|---|---|---|---|
| Current password | `old_password` | `password` | Required |
| New password | `new_password` | `password` | `minlength: 8`, `maxlength: 72` |
| Confirm password | `confirm_password` | `password` | Required |

**POST target:** `/profile/change-password`

**Strength indicators** (shown below the new password field):

| Indicator ID | Rule |
|---|---|
| `#pw-length` | 8–72 characters |
| `#pw-letter` | At least one letter |
| `#pw-number` | At least one number |
| `#pw-special` | At least one special character (`!@#$%^&*…`) |

Validation logic lives in `/static/js/profile.js`. Errors render in `#profile-error` (`.msg-error.d-none` by default).

---

## 8. Responsive Behaviour

| Breakpoint | Layout change |
|---|---|
| `≥ 769px` | Two-column grid as specified |
| `≤ 768px` | Single column; sidebar stacks above right panel; sidebar `position: relative`, height `auto` |

---

## 9. File Structure

```
/templates/
  profile.html          ← Main template (extends index.html)

/static/
  css/
    profile.css         ← All layout + component styles for this page
  js/
    profile.js          ← Password strength validation, form error handling
```

**External dependencies:**

| Library | Source | Usage |
|---|---|---|
| Bootstrap 5 | CDN (inherited from `index.html`) | Grid utilities, table, badge, form |
| Chart.js | `cdn.jsdelivr.net/npm/chart.js` | Bar + pie charts |

---

## 10. Accessibility Notes

- Avatar circle must include `aria-label="User avatar"`.
- Navigation links must be wrapped in a `<nav>` element with `aria-label="Profile navigation"`.
- Password inputs must have explicit `<label>` elements or `aria-label` attributes.
- Chart canvases should include `aria-label` describing the chart type and data source.
- Cover edit button must have `aria-label="Edit cover image"`.

---

## 11. Out of Scope (v1)

- Cover image upload and crop functionality.
- Dashboard settings content (nav link present, panel content TBD).
- Account settings sub-page (nav link present, route TBD).
- Avatar image upload (initials-only in v1).
- Two-factor authentication settings.

---

## 12. Open Questions

| # | Question | Owner |
|---|---|---|
| 1 | What does the "Dashboard settings" section contain? | Yash |
| 2 | Should the cover banner support gradient presets as an alternative to image upload? | Yash |
| 3 | Is the "edit" button on the avatar circle in scope for v1? | Yash |