from flask import Flask, render_template, request, redirect, make_response, flash, jsonify
from datetime import datetime, timedelta, timezone
from Database.db import get_db, init_db, CATEGORIES
from Database.auth import verify_password, create_token, decode_token, get_user_by_email, create_user, get_user_by_id
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default-secret-key-change-me")


def get_current_user():
    session = request.cookies.get("session")
    if not session:
        return None
    payload = decode_token(session)
    if not payload:
        return None
    return get_user_by_id(payload.get("user_id"))


def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def index():
    return redirect("/landing")


@app.route("/landing")
def landing():
    if get_current_user():
        return redirect("/dashboard")
    error = request.args.get("error", "")
    card = request.args.get("card", "login")
    return render_template("landing.html", error=error, card=card)


@app.route("/auth/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    remember = request.form.get("remember_me")

    if not email or not password:
        return redirect("/landing?error=Email+and+password+are+required")

    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return redirect("/landing?error=Email+or+password+does+not+match&card=login")

    token = create_token(user["id"])

    max_age = 60 * 60 * 24 * 7 if remember else 60 * 60 * 24
    resp = make_response(redirect("/dashboard"))
    resp.set_cookie("session", token, httponly=True, samesite="lax", max_age=max_age)
    return resp


@app.route("/auth/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    if not name or not email or not password:
        return redirect("/landing?error=All+fields+are+required&card=register")

    if password != confirm:
        return redirect("/landing?error=Passwords+do+not+match&card=register")

    success, error = create_user(name, email, password)
    if not success:
        return redirect(f"/landing?error={error.replace(' ', '+')}&card=register")

    user = get_user_by_email(email)
    token = create_token(user["id"])

    resp = make_response(redirect("/dashboard"))
    resp.set_cookie("session", token, httponly=True, samesite="lax", max_age=60 * 60 * 24)
    return resp


@app.route("/auth/logout", methods=["POST"])
def logout():
    resp = make_response(redirect("/landing"))
    resp.delete_cookie("session")
    return resp


@app.route("/profile")
@require_auth
def profile():
    user = get_current_user()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id = ?", (user["id"],))
    total_spent = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM expenses WHERE user_id = ?", (user["id"],))
    transaction_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
        (user["id"],)
    )
    category_rows = cursor.fetchall()
    category_totals = {row["category"]: row["total"] for row in category_rows}
    top_category = category_rows[0]["category"] if category_rows else "N/A"

    cursor.execute(
        "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC, created_at DESC LIMIT 5",
        (user["id"],)
    )
    recent_transactions = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        "SELECT AVG(amount) as avg, MAX(amount) as max, MIN(amount) as min FROM expenses WHERE user_id = ?",
        (user["id"],))
    stats_row = cursor.fetchone()
    avg_spent = round(stats_row["avg"] or 0, 2) if stats_row else 0
    max_spent = round(stats_row["max"] or 0, 2) if stats_row else 0
    min_spent = round(stats_row["min"] or 0, 2) if stats_row else 0

    chart_data = {"category_totals": category_totals}

    conn.close()

    return render_template("profile.html", user=user, categories=CATEGORIES,
                           total_spent=total_spent, transaction_count=transaction_count,
                           top_category=top_category, category_totals=category_totals,
                           recent_transactions=recent_transactions,
                           avg_spent=avg_spent, max_spent=max_spent, min_spent=min_spent,
                           chart_data=chart_data)


@app.route("/dashboard")
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


@app.route("/api/chart-data")
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


@app.route("/add", methods=["POST"])
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


@app.route("/remove", methods=["POST"])
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


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)