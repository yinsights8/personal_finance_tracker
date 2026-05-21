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
| Route        | Template          | Notes |
|--------------|-------------------|-------|
| `/dashboard` | `templates/index.html` | Main expense table; data injected as `data` (list of lists) |
| `/profile`   | `templates/profile.html` | Summary stats already passed from Python |

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
import json
chart_data = json.dumps({
    "category_totals": dict(category_rows),
    "monthly": monthly_rows,
    ...
})
return render_template("index.html", ..., chart_data=chart_data)
```

**In Jinja2 template:**
```html
<script>
  const CHART_DATA = {{ chart_data | tojson }};
</script>
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
- Tooltips must show `£` prefix and 2 decimal places
- Weekly/Monthly/Yearly toggle: use Bootstrap button group, update chart data with `.update()` not re-render
- Chart containers should be wrapped in `<div style="position:relative; height:300px;">`
- Use Chart.js v3+ syntax (`scales.x`, `scales.y` — not `xAxes[]`)

---

## KPI Cards

Always display these four KPI cards above charts:

```html
<div class="row g-3 mb-4">
  <div class="col-6 col-md-3">
    <div class="card text-center shadow-sm">
      <div class="card-body">
        <div class="text-muted small">Total Spent</div>
        <div class="fw-bold fs-4">£{{ "%.2f"|format(total_spent) }}</div>
      </div>
    </div>
  </div>
  <!-- repeat for Average, Max, Min -->
</div>
```

---

## Integration Checklist

When adding or updating analytics:

1. **Add SQL queries** in the route handler (`app.py`) — always filter by `user_id`
2. **Inject `chart_data` JSON** via `render_template()`
3. **Add `<canvas>` elements** with unique IDs in the template
4. **Load Chart.js** from CDN if not already present: `https://cdn.jsdelivr.net/npm/chart.js`
5. **Initialise charts** in a `<script>` block at bottom of template body
6. **Add toggle buttons** for time-period switching on the vertical bar chart
7. **Test with empty data** — always guard against `null`/empty arrays before rendering

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