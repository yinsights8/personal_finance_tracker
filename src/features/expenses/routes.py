from flask import Blueprint, render_template, request, redirect, jsonify
from datetime import datetime

from shared.db import get_db, CATEGORIES
from features.auth.routes import require_auth, get_current_user

expenses_bp = Blueprint("expenses", __name__)


@expenses_bp.route("/dashboard")
@require_auth
def dashboard():
    user = get_current_user()
    conn = get_db()
    cursor = conn.cursor()

    month_year = datetime.now().strftime("%B %Y")
    cursor.execute(
        "SELECT category, amount, date, description, created_at, id FROM expenses WHERE user_id = ? ORDER BY date DESC",
        (user["id"],)
    )
    rows = cursor.fetchall()
    data = [list(row) for row in rows]

    total = sum(row[1] for row in data) if data else 0

    category_totals = {}
    weekly = []
    monthly = []
    yearly = []
    stats = {"avg": 0, "max": 0, "min": 0, "total": 0}

    if data:
        cursor.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
            (user["id"],))
        category_totals = {row["category"]: row["total"] for row in cursor.fetchall()}

        cursor.execute(
            "SELECT strftime('%Y-W%W', date) as period, SUM(amount) as total FROM expenses WHERE user_id = ? AND date >= date('now', '-56 days') GROUP BY period ORDER BY period ASC",
            (user["id"],))
        weekly = [{"period": r["period"], "total": r["total"]} for r in cursor.fetchall()]

        cursor.execute(
            "SELECT strftime('%Y-%m', date) as period, SUM(amount) as total FROM expenses WHERE user_id = ? AND date >= date('now', '-365 days') GROUP BY period ORDER BY period ASC",
            (user["id"],))
        monthly = [{"period": r["period"], "total": r["total"]} for r in cursor.fetchall()]

        cursor.execute(
            "SELECT strftime('%Y', date) as period, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY period ORDER BY period ASC",
            (user["id"],))
        yearly = [{"period": r["period"], "total": r["total"]} for r in cursor.fetchall()]

        cursor.execute(
            "SELECT AVG(amount) as avg, MAX(amount) as max, MIN(amount) as min, SUM(amount) as total FROM expenses WHERE user_id = ?",
            (user["id"],))
        stats_row = cursor.fetchone()
        stats = {"avg": round(stats_row["avg"] or 0, 2), "max": round(stats_row["max"] or 0, 2), "min": round(stats_row["min"] or 0, 2), "total": round(stats_row["total"] or 0, 2)}

    chart_data = {
        "category_totals": category_totals,
        "weekly": weekly,
        "monthly": monthly,
        "yearly": yearly,
        "stats": stats,
    }

    conn.close()

    return render_template("index.html", data=data, categories=CATEGORIES, total_expenses=total, month_year=month_year, user=user, chart_data=chart_data, stats=stats)


@expenses_bp.route("/api/chart-data")
@require_auth
def api_chart_data():
    user = get_current_user()
    date_from = request.args.get("from", "")
    date_to = request.args.get("to", "")
    conn = get_db()
    cursor = conn.cursor()

    conditions = ["user_id = ?"]
    params = [user["id"]]
    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)

    where = " AND ".join(conditions)

    cursor.execute(
        f"SELECT category, SUM(amount) as total FROM expenses WHERE {where} GROUP BY category ORDER BY total DESC",
        params)
    category_totals = {row["category"]: row["total"] for row in cursor.fetchall()}

    cursor.execute(
        f"SELECT strftime('%Y-W%W', date) as period, SUM(amount) as total FROM expenses WHERE {where} AND date >= date('now', '-56 days') GROUP BY period ORDER BY period ASC",
        params)
    weekly = [{"period": r["period"], "total": r["total"]} for r in cursor.fetchall()]

    cursor.execute(
        f"SELECT strftime('%Y-%m', date) as period, SUM(amount) as total FROM expenses WHERE {where} AND date >= date('now', '-365 days') GROUP BY period ORDER BY period ASC",
        params)
    monthly = [{"period": r["period"], "total": r["total"]} for r in cursor.fetchall()]

    cursor.execute(
        f"SELECT strftime('%Y', date) as period, SUM(amount) as total FROM expenses WHERE {where} GROUP BY period ORDER BY period ASC",
        params)
    yearly = [{"period": r["period"], "total": r["total"]} for r in cursor.fetchall()]

    cursor.execute(
        f"SELECT AVG(amount) as avg, MAX(amount) as max, MIN(amount) as min, SUM(amount) as total FROM expenses WHERE {where}",
        params)
    row = cursor.fetchone()
    stats = {"avg": round(row["avg"] or 0, 2), "max": round(row["max"] or 0, 2), "min": round(row["min"] or 0, 2), "total": round(row["total"] or 0, 2)}

    conn.close()

    return jsonify({
        "category_totals": category_totals,
        "weekly": weekly,
        "monthly": monthly,
        "yearly": yearly,
        "stats": stats,
    })


@expenses_bp.route("/add", methods=["POST"])
@require_auth
def add_expense():
    user = get_current_user()
    category = request.form.get("name")
    amount = request.form.get("price")
    description = request.form.get("description", "")

    if not category or not amount:
        return redirect("/dashboard")

    try:
        amount = float(amount)
    except ValueError:
        return redirect("/dashboard")

    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        (user["id"], amount, category, today, description)
    )
    conn.commit()
    conn.close()

    return redirect("/dashboard")


@expenses_bp.route("/remove", methods=["POST"])
@require_auth
def remove_expense():
    user = get_current_user()
    items = request.form.getlist("items")

    if not items:
        return redirect("/dashboard")

    conn = get_db()
    cursor = conn.cursor()

    for item in items:
        parts = item.split(",")
        if len(parts) >= 4:
            category = parts[0]
            amount = float(parts[1])
            date = parts[2]
            description = parts[3] if len(parts) > 3 else ""

            cursor.execute(
                "DELETE FROM expenses WHERE user_id = ? AND category = ? AND amount = ? AND date = ? AND COALESCE(description, '') = ?",
                (user["id"], category, amount, date, description)
            )

    conn.commit()
    conn.close()

    return redirect("/dashboard")
