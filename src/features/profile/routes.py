from flask import Blueprint, render_template

from shared.db import get_db, CATEGORIES
from features.auth.routes import require_auth, get_current_user

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
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
