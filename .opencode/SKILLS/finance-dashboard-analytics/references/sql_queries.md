# SQL Query Patterns — Expense Analytics

All queries filter by `user_id`. Date column is stored as TEXT in `YYYY-MM-DD` format — SQLite's `strftime()` works correctly on this.

---

## Weekly Aggregations

```sql
-- Last 8 weeks, grouped by ISO week
SELECT
  strftime('%Y-W%W', date) AS period,
  SUM(amount)              AS total,
  COUNT(*)                 AS count
FROM expenses
WHERE user_id = ?
  AND date >= date('now', '-56 days')
GROUP BY period
ORDER BY period ASC;

-- Current week only
SELECT SUM(amount) AS weekly_total
FROM expenses
WHERE user_id = ?
  AND strftime('%Y-%W', date) = strftime('%Y-%W', 'now');
```

---

## Monthly Aggregations

```sql
-- Last 12 months
SELECT
  strftime('%Y-%m', date) AS period,
  SUM(amount)             AS total,
  COUNT(*)                AS count
FROM expenses
WHERE user_id = ?
  AND date >= date('now', '-365 days')
GROUP BY period
ORDER BY period ASC;

-- Current month only
SELECT SUM(amount) AS monthly_total
FROM expenses
WHERE user_id = ?
  AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now');

-- Month-over-month comparison
SELECT
  strftime('%Y-%m', date) AS month,
  SUM(amount)             AS total
FROM expenses
WHERE user_id = ?
GROUP BY month
ORDER BY month DESC
LIMIT 2;
```

---

## Yearly Aggregations

```sql
-- All years
SELECT
  strftime('%Y', date) AS period,
  SUM(amount)          AS total,
  COUNT(*)             AS count
FROM expenses
WHERE user_id = ?
GROUP BY period
ORDER BY period ASC;

-- Current year only
SELECT SUM(amount) AS yearly_total
FROM expenses
WHERE user_id = ?
  AND strftime('%Y', date) = strftime('%Y', 'now');
```

---

## Category Breakdown with Period Filter

```sql
-- Category totals for current month
SELECT
  category,
  SUM(amount)  AS total,
  COUNT(*)     AS count,
  AVG(amount)  AS avg_per_entry
FROM expenses
WHERE user_id = ?
  AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
GROUP BY category
ORDER BY total DESC;

-- Category totals for a specific month (pass as parameter)
-- e.g. period = '2025-01'
SELECT category, SUM(amount) AS total
FROM expenses
WHERE user_id = ?
  AND strftime('%Y-%m', date) = ?
GROUP BY category;
```

---

## Stats (Avg / Max / Min)

```sql
-- All-time stats
SELECT
  AVG(amount) AS avg_amount,
  MAX(amount) AS max_amount,
  MIN(amount) AS min_amount,
  SUM(amount) AS total_amount,
  COUNT(*)    AS transaction_count
FROM expenses
WHERE user_id = ?;

-- Monthly stats (for a given month)
SELECT
  AVG(amount) AS avg_amount,
  MAX(amount) AS max_amount,
  MIN(amount) AS min_amount
FROM expenses
WHERE user_id = ?
  AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now');
```

---

## Python Helper — Build chart_data dict

```python
import json
from datetime import datetime

def build_chart_data(cursor, user_id: int) -> str:
    """Returns JSON string safe to inject into Jinja2 template via tojson."""

    # Category totals
    cursor.execute("""
        SELECT category, SUM(amount) as total FROM expenses
        WHERE user_id = ? GROUP BY category ORDER BY total DESC
    """, (user_id,))
    category_totals = {row["category"]: row["total"] for row in cursor.fetchall()}

    # Weekly (last 8 weeks)
    cursor.execute("""
        SELECT strftime('%Y-W%W', date) as period, SUM(amount) as total
        FROM expenses WHERE user_id = ? AND date >= date('now', '-56 days')
        GROUP BY period ORDER BY period ASC
    """, (user_id,))
    weekly = [{"period": r["period"], "total": r["total"]} for r in cursor.fetchall()]

    # Monthly (last 12 months)
    cursor.execute("""
        SELECT strftime('%Y-%m', date) as period, SUM(amount) as total
        FROM expenses WHERE user_id = ? AND date >= date('now', '-365 days')
        GROUP BY period ORDER BY period ASC
    """, (user_id,))
    monthly = [{"period": r["period"], "total": r["total"]} for r in cursor.fetchall()]

    # Yearly
    cursor.execute("""
        SELECT strftime('%Y', date) as period, SUM(amount) as total
        FROM expenses WHERE user_id = ?
        GROUP BY period ORDER BY period ASC
    """, (user_id,))
    yearly = [{"period": r["period"], "total": r["total"]} for r in cursor.fetchall()]

    # Stats
    cursor.execute("""
        SELECT AVG(amount) as avg, MAX(amount) as max,
               MIN(amount) as min, SUM(amount) as total
        FROM expenses WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    stats = {
        "avg":   round(row["avg"]   or 0, 2),
        "max":   round(row["max"]   or 0, 2),
        "min":   round(row["min"]   or 0, 2),
        "total": round(row["total"] or 0, 2),
    }

    return {
        "category_totals": category_totals,
        "weekly":  weekly,
        "monthly": monthly,
        "yearly":  yearly,
        "stats":   stats,
    }
```