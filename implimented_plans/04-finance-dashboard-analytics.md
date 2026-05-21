# Finance Dashboard Analytics — Implementation Plan

## Overview

Add 5 chart/analytics features across Dashboard (`/dashboard` → `index.html`) and Profile (`/profile` → `profile.html`) pages. Currently zero Chart.js usage exists. Reference files (`.opencode/SKILLS/finance-dashboard-analytics/references/`) contain complete, ready-to-copy code for SQL queries and Chart.js patterns.

## Files to Modify

| File | Change |
|------|--------|
| `app.py` | Add analytics SQL queries to `/dashboard` and `/profile` routes; inject `chart_data` JSON + KPI stats |
| `templates/index.html` | Add Chart.js CDN, KPI cards, canvas elements, toggle buttons, script block with 4 charts |
| `templates/profile.html` | Add Chart.js CDN, KPI cards (avg/max/min), canvas elements, script block with 2 charts |

## Decisions Made (per user)

| Decision | Choice |
|----------|--------|
| Template structure | Keep current approach — Chart.js CDN in scripts block |
| Currency | `₹` (Rupee) — match existing app |
| App file | `app.py` only (not `test.py`) |

---

## Step 1: `app.py` — `/dashboard` route

Add 5 SQL queries between fetching expenses rows and `conn.close()`:

1. **Category totals** — `SELECT category, SUM(amount) ... GROUP BY category ORDER BY total DESC`
2. **Weekly** — Last 8 weeks: `strftime('%Y-W%W', date)` with `date >= date('now', '-56 days')`
3. **Monthly** — Last 12 months: `strftime('%Y-%m', date)` with `date >= date('now', '-365 days')`
4. **Yearly** — All years: `strftime('%Y', date)` 
5. **Stats** — `AVG, MAX, MIN, SUM` for KPI cards

Build `chart_data` dict with all 5 results, serialize to JSON. Pass `chart_data` + `stats` dict to `render_template`.

---

## Step 2: `app.py` — `/profile` route

Add 1 stats query (`AVG, MAX, MIN`) after the existing `category_totals` query.

Pass `chart_data` (JSON with `category_totals`), `avg_spent`, `max_spent`, `min_spent` to `render_template`.

---

## Step 3: `templates/index.html`

### 3a. Chart.js CDN
Add `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>` in `<head>`.

### 3b. Analytics Section (wrapped in `<div id="analyticsSection">`)

**KPI Cards** (4 cards in a `.row.g-3.mb-4`):
- Total Spent
- Avg per Entry
- Highest
- Lowest

**Horizontal Bar Chart** — Spending by Category:
- `indexAxis: "y"`, colored by `CATEGORY_COLORS`, border-radius 6

**Pie Chart** — Category Share:
- Percentage in tooltips, legend on right

**Time Series Chart** with toggle buttons:
- Bootstrap btn-group: [Weekly] [Monthly] [Yearly]
- Timeline overlay checkbox: "Show Trend Line"
- Running total trend line toggled via `.update()` (not re-render)

### 3c. Script Block

- `const CHART_DATA = {{ chart_data \| tojson }};`
- `CATEGORY_COLORS` map (with `₹` in tooltips, not `£`)
- Empty-state guard:
  ```js
  if (!CHART_DATA.category_totals || Object.keys(CHART_DATA.category_totals).length === 0) {
    document.getElementById("analyticsSection").innerHTML =
      `<div class="text-center text-muted py-5">No expenses yet — add some to see analytics.</div>`;
  }
  ```
- All chart initializations inside the guard
- Period toggle event handler (updates datasets via `.update()`)
- Timeline toggle event handler

---

## Step 4: `templates/profile.html`

### 4a. Chart.js CDN
Add in `{% block scripts %}` before `main_profile.js`.

### 4b. KPI Cards
Replace/expand the existing summary stats into all 4 KPI cards (Total, Avg, Max, Min) with the same card styling.

### 4c. Chart Canvases
Add two new `<div class="profile-card">` sections:
1. **Horizontal Bar Chart** — Spending by Category (`canvas id="categoryBarChart"`)
2. **Pie Chart** — Category Share (`canvas id="categoryPieChart"`)

### 4d. Script Block
- `const CHART_DATA = {{ chart_data \| tojson }};`
- `CATEGORY_COLORS` map
- Empty-state guard
- Horizontal bar + pie chart initialization

---

## Charts Mapping

| Chart | Dashboard | Profile |
|-------|:---------:|:-------:|
| KPI Cards (Total, Avg, Max, Min) | ✅ New | ✅ Avg/Max/Min new + existing Total |
| Horizontal Bar — Category | ✅ New | ✅ New |
| Pie — Category Share | ✅ New | ✅ New |
| Vertical Bar — Time Series (W/M/Y) + Timeline Overlay | ✅ New | ❌ |

All charts use `responsive: true`, `maintainAspectRatio: false`, canvases wrapped in `<div style="position:relative; height:300px;">`. Tooltips show `₹` prefix with 2 decimal places.

## Edge Cases

- **Empty state**: Guard checks `CHART_DATA.category_totals` keys length before rendering
- **Missing category colors**: Fallback to `"#C9CBCF"` via `||`
- **Zero stats**: SQLite returns `None` → handled with `or 0`
- **Empty time series**: Empty arrays produce empty chart display

## Verification

```bash
cd "E:\ClaudeCode learning\expence_tracker\personal_finance_tracker"
python app.py
```

Check:
- Dashboard shows 4 KPI cards with correct ₹ values
- Dashboard shows 3 charts (horizontal bar, pie, time series)
- Period toggle switches weekly/monthly/yearly
- Timeline overlay toggles trend line
- Profile shows expanded KPI cards + 2 charts
- Empty state renders correctly for new user with no expenses
