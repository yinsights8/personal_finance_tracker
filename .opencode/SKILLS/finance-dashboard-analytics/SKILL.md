---
name: finance-dashboard-analytics

description: >
  Skill for building interactive analytics dashboards for the personal_finance_tracker app
  (github.com/yinsights8/personal_finance_tracker). Use this skill whenever Yash asks to:
  build, update, or improve any chart, graph, or analytics view in the finance tracker;
  display spending breakdowns by category; add analytics to the dashboard (/dashboard route)
  or user profile (/profile route); visualise weekly/monthly/yearly spending; show KPI stats
  like average/max/min spend; generate chart code targeting the Flask + SQLite (expense_tracker.db)
  stack; or any request involving Chart.js, spending trends, or expense visualisation.
  Always use this skill even if the request sounds simple, like "add a pie chart" or "show me monthly spending".
---

# Finance Dashboard Analytics Skill

## Project Context

**Repo:** `github.com/yinsights8/personal_finance_tracker`
**Stack:** Flask (Python), SQLite (`expense_tracker.db`), Jinja2 templates, vanilla JS + Chart.js, Bootstrap

### Database Schema

```sql
-- expenses table
CREATE TABLE expenses (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id     INTEGER NOT NULL,
  amount      REAL    NOT NULL,
  category    TEXT    NOT NULL,
  date        TEXT    NOT NULL,  -- stored as 'YYYY-MM-DD' string
  description TEXT,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- users table
CREATE TABLE users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT    NOT NULL,
  email         TEXT    UNIQUE NOT NULL,
  password_hash TEXT    NOT NULL,
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Categories (canonical list)
```python
CATEGORIES = ["Food", "Transport", "Bills", "Health", "Movie tickets", "Shopping", "Other"]
```

### Category Colour Palette (use consistently)
```js
const CATEGORY_COLORS = {
  "Food":          "#FF6384",
  "Transport":     "#36A2EB",
  "Bills":         "#FFCE56",
  "Health":        "#4BC0C0",
  "Movie tickets": "#9966FF",
  "Shopping":      "#FF9F40",
  "Other":         "#C9CBCF"
};
```

### Routes that surface analytics
| Route              | Template/Type        | Notes |
|--------------------|----------------------|-------|
| `/dashboard`       | `templates/index.html` | Main expense table; data injected as `data` (list of lists); `chart_data` JSON + `stats` dict for analytics |
| `/profile`         | `templates/profile.html` | Summary stats + `chart_data` JSON for profile charts |
| `/api/chart-data`  | JSON API              | `GET ?from=&to=` — returns filtered `category_totals`, `weekly`, `monthly`, `yearly`, `stats`. JWT auth required. |

---

## Analytics Architecture

### Python-side data preparation (in `app.py` route handlers)

Always query with `user_id` filter. Aggregate in SQL where possible — don't pull all rows and aggregate in Python.

**Standard query patterns:**

```python
# Weekly totals (last 4 weeks)
cursor.execute("""
  SELECT strftime('%Y-W%W', date) as week, SUM(amount) as total
  FROM expenses WHERE user_id = ?
  GROUP BY week ORDER BY week DESC LIMIT 4
""", (user_id,))

# Monthly totals (last 12 months)
cursor.execute("""
  SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
  FROM expenses WHERE user_id = ?
  GROUP BY month ORDER BY month DESC LIMIT 12
""", (user_id,))

# Yearly totals
cursor.execute("""
  SELECT strftime('%Y', date) as year, SUM(amount) as total
  FROM expenses WHERE user_id = ?
  GROUP BY year ORDER BY year DESC
""", (user_id,))

# Category breakdown
cursor.execute("""
  SELECT category, SUM(amount) as total, COUNT(*) as count
  FROM expenses WHERE user_id = ?
  GROUP BY category ORDER BY total DESC
""", (user_id,))

# Stats (avg / max / min) — pass period filter as needed
cursor.execute("""
  SELECT
    AVG(amount) as avg_amount,
    MAX(amount) as max_amount,
    MIN(amount) as min_amount
  FROM expenses WHERE user_id = ?
""", (user_id,))
```

**Inject data as JSON into templates:**
```python
chart_data = {
    "category_totals": dict(category_rows),
    "monthly": monthly_rows,
    ...
}
return render_template("index.html", ..., chart_data=chart_data)
```

**In Jinja2 template (use `| tojson` — pass Python dict, NOT `json.dumps()` string):**
```html
<script>
  const CHART_DATA = {{ chart_data | tojson }};
</script>
```

---

## API Endpoint — `/api/chart-data`

**Route:** `GET /api/chart-data?from=YYYY-MM-DD&to=YYYY-MM-DD`
**Auth:** `@require_auth` (JWT session cookie)
**Purpose:** Returns analytics data filtered by optional date range. Called client-side when the date filter changes.

### Query params

| Param  | Required | Description |
|--------|----------|-------------|
| `from` | No       | Lower bound (inclusive): `date >= ?` |
| `to`   | No       | Upper bound (inclusive): `date <= ?` |

### Response format (JSON)

```json
{
  "category_totals": { "Food": 120.5, "Transport": 45.0, ... },
  "weekly":  [{"period": "2026-W20", "total": 210.5}, ...],
  "monthly": [{"period": "2026-05", "total": 890.0}, ...],
  "yearly":  [{"period": "2026", "total": 3200.0}, ...],
  "stats": { "avg": 45.20, "max": 150.00, "min": 5.00, "total": 3200.00 }
}
```

### Dynamic WHERE clause pattern

```python
conditions = ["user_id = ?"]
params = [user["id"]]
if date_from:
    conditions.append("date >= ?")
    params.append(date_from)
if date_to:
    conditions.append("date <= ?")
    params.append(date_to)

where = " AND ".join(conditions)
# Used: f"SELECT ... FROM expenses WHERE {where} GROUP BY ..."
# The {where} is safe — only hardcoded column names and param placeholders
```

### Called from `main.js`

```javascript
function fetchAndUpdateAnalytics() {
    var dateFrom = document.getElementById('dateFrom').value;
    var dateTo = document.getElementById('dateTo').value;
    var params = new URLSearchParams();
    if (dateFrom) params.set('from', dateFrom);
    if (dateTo) params.set('to', dateTo);
    var qs = params.toString();
    fetch('/api/chart-data' + (qs ? '?' + qs : ''))
        .then(function(r) { return r.json(); })
        .then(function(data) { window.updateAnalyticsFromData(data); });
}
```

---

## Dashboard Table Features

### Date Range Filter

Two `<input type="date">` fields above the table, labeled "Select dates". Filtering is client-side with a "Clear" button to reset.

```html
<div class="d-flex align-items-center gap-2 mb-2 flex-wrap">
    <label class="text-light small fw-semibold">Select dates</label>
    <input type="date" id="dateFrom" ...>
    <span class="text-muted small">to</span>
    <input type="date" id="dateTo" ...>
    <button class="btn btn-sm btn-outline-secondary" id="clearDates">Clear</button>
</div>
```

### Pagination

- 5 rows per page (`ROWS_PER_PAGE = 5`)
- `<< Previous` / `Next >>` buttons at bottom-right
- Buttons disabled when at first/last page
- Info text: `1–5 of 20`

Table rows include `data-date="{{row[2]}}"` attribute for JS date filtering.

### JS functions (in `static/main.js`)

| Function | Purpose |
|----------|---------|
| `getFilteredRows()` | Returns visible `<tr>` elements matching the date range |
| `updatePagination()` | Shows only 5 rows for current page, updates button states |
| `fetchAndUpdateAnalytics()` | Calls `/api/chart-data` and passes result to chart update function |

---

## Live Chart Updates

When the date range filter changes, analytics must update without a full page reload.

### Global references (set in `index.html` script block)

```javascript
window.categoryBarChart  // Horizontal bar chart instance
window.categoryPieChart  // Pie chart instance
window.timeSeriesChart   // Time series chart instance
window.currentPeriod     // "weekly" | "monthly" | "yearly"
window.showTrend         // boolean — timeline overlay
```

### Single update function

```javascript
window.updateAnalyticsFromData = function(newChartData) {
    // 1. Update KPI cards (by ID)
    document.getElementById("kpiTotal").textContent = '₹' + newChartData.stats.total.toFixed(2);
    document.getElementById("kpiAvg").textContent   = '₹' + newChartData.stats.avg.toFixed(2);
    document.getElementById("kpiMax").textContent   = '₹' + newChartData.stats.max.toFixed(2);
    document.getElementById("kpiMin").textContent   = '₹' + newChartData.stats.min.toFixed(2);
    document.getElementById("totalExpensesDisplay").textContent = 'Total Expenses: ₹' + newChartData.stats.total.toFixed(2);

    // 2. Update horizontal bar chart
    var labels = Object.keys(newChartData.category_totals);
    var values = Object.values(newChartData.category_totals);
    var colors = labels.map(function(l) { return CATEGORY_COLORS[l] || "#C9CBCF"; });
    window.categoryBarChart.data.labels = labels;
    window.categoryBarChart.data.datasets[0].data = values;
    window.categoryBarChart.data.datasets[0].backgroundColor = colors;
    window.categoryBarChart.update();

    // 3. Update pie chart
    window.categoryPieChart.data.labels = labels;
    window.categoryPieChart.data.datasets[0].data = values;
    window.categoryPieChart.data.datasets[0].backgroundColor = colors;
    window.categoryPieChart.update();

    // 4. Update time series chart (uses current period + trend state)
    var tsData = buildTimeDatasets(newChartData[window.currentPeriod], window.showTrend);
    window.timeSeriesChart.data.labels = tsData.labels;
    window.timeSeriesChart.data.datasets = tsData.datasets;
    window.timeSeriesChart.update();
};
```

### Flow

```
Date filter change
  → updatePagination()  (table rows)
  → fetchAndUpdateAnalytics()
    → GET /api/chart-data?from=X&to=Y
    → window.updateAnalyticsFromData(response)
      → KPI cards updated
      → All 3 charts updated with .update()
```

---

## Chart Specifications

Read `references/charts.md` for detailed Chart.js implementation code for each chart type.

### Required Charts

| # | Chart | Location | Description |
|---|-------|----------|-------------|
| 1 | **Horizontal Bar — by Category** | Dashboard + Profile | Total spend per category, sorted descending. Use `CATEGORY_COLORS`. |
| 2 | **Pie — Category Share** | Dashboard + Profile | Percentage of total per category. Show % labels. Use `CATEGORY_COLORS`. |
| 3 | **Vertical Bar — Time Series** | Dashboard | Toggle between Weekly / Monthly / Yearly via button group. Single colour (`#36A2EB`). |
| 4 | **KPI Cards** | Dashboard + Profile | Total, Average, Max, Min — as styled stat cards above the charts. |
| 5 | **Timeline Overlay** | Dashboard | A line drawn on top of the Vertical Bar chart showing the running total trend. Toggle-able. |

### Interactivity Rules
- All charts must have `responsive: true` and `maintainAspectRatio: false`
- Tooltips must show `₹` prefix and 2 decimal places
- Weekly/Monthly/Yearly toggle: use Bootstrap button group, update chart data with `.update()` not re-render
- Chart containers should be wrapped in `<div style="position:relative; height:300px;">`
- Use Chart.js v3+ syntax (`scales.x`, `scales.y` — not `xAxes[]`)
- Chart instances and state must be stored on `window` for live updates (`window.categoryBarChart`, `window.currentPeriod`, etc.)

---

## KPI Cards

Always display these four KPI cards above charts. Values use element IDs so they can be updated live via `window.updateAnalyticsFromData()`.

```html
<div class="row g-3 mb-4">
  <div class="col-6 col-md-3">
    <div class="card text-center shadow-sm h-100">
      <div class="card-body py-3">
        <div class="text-muted small fw-semibold">Total Spent</div>
        <div class="fw-bold fs-4 mt-1" id="kpiTotal">₹{{ "%.2f"|format(stats.total) }}</div>
      </div>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card text-center shadow-sm h-100">
      <div class="card-body py-3">
        <div class="text-muted small fw-semibold">Avg per Entry</div>
        <div class="fw-bold fs-4 mt-1" id="kpiAvg">₹{{ "%.2f"|format(stats.avg) }}</div>
      </div>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card text-center shadow-sm h-100">
      <div class="card-body py-3">
        <div class="text-muted small fw-semibold">Highest</div>
        <div class="fw-bold fs-4 mt-1" id="kpiMax">₹{{ "%.2f"|format(stats.max) }}</div>
      </div>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card text-center shadow-sm h-100">
      <div class="card-body py-3">
        <div class="text-muted small fw-semibold">Lowest</div>
        <div class="fw-bold fs-4 mt-1" id="kpiMin">₹{{ "%.2f"|format(stats.min) }}</div>
      </div>
    </div>
  </div>
</div>
```

The `stats` dict is passed from the Python route:
```python
cursor.execute("SELECT AVG(amount) as avg, MAX(amount) as max, MIN(amount) as min, SUM(amount) as total FROM expenses WHERE user_id = ?", (user_id,))
row = cursor.fetchone()
stats = {"avg": round(row["avg"] or 0, 2), "max": round(row["max"] or 0, 2), "min": round(row["min"] or 0, 2), "total": round(row["total"] or 0, 2)}
```

---

## Integration Checklist

When adding or updating analytics:

1. **Add SQL queries** in the route handler (`app.py`) — always filter by `user_id`
2. **Inject `chart_data` dict** via `render_template()` (NOT `json.dumps()` — use `| tojson` in template)
3. **Inject `stats` dict** for KPI cards (avg, max, min, total)
4. **Add `<canvas>` elements** with unique IDs in the template
5. **Add IDs to KPI values** (`kpiTotal`, `kpiAvg`, `kpiMax`, `kpiMin`) and total expenses (`totalExpensesDisplay`)
6. **Load Chart.js** from CDN if not already present: `https://cdn.jsdelivr.net/npm/chart.js`
7. **Initialise charts** in a `<script>` block at bottom of template body
8. **Store chart instances on `window`** for live update access
9. **Add `window.updateAnalyticsFromData(data)`** to update all charts + KPI cards + total when new data arrives
10. **Add `/api/chart-data` endpoint** when live date filter updates are needed
11. **Add toggle buttons** for time-period switching on the vertical bar chart
12. **Test with empty data** — always guard against `null`/empty arrays before rendering

---

## Output Format

When asked to implement analytics:

1. **List the changes** — which files are touched and why
2. **Provide Python snippet** (route handler additions)
3. **Provide HTML snippet** (canvas elements + KPI card markup)
4. **Provide JS snippet** (Chart.js initialisation + toggle logic)
5. Keep snippets clearly labelled with the file they belong to

If a full file rewrite is needed, output the complete file.

---

## References

- `references/charts.md` — Full Chart.js code for each of the 5 chart types
- `references/sql_queries.md` — Extended SQL patterns for time filtering