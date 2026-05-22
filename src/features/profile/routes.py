from flask import Blueprint, render_template, request, jsonify

from shared.db import get_db, CATEGORIES
from features.auth.routes import require_auth, get_current_user
from features.auth.service import validate_password, hash_password, verify_password

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


@profile_bp.route("/profile/change-password", methods=["POST"])
@require_auth
def change_password():
    user = get_current_user()
    old_password = request.form.get("old_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not old_password or not new_password or not confirm_password:
        return jsonify({"ok": False, "error": "All fields are required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user["id"],))
    row = cursor.fetchone()

    if not row or not verify_password(old_password, row["password_hash"]):
        conn.close()
        return jsonify({"ok": False, "error": "Current password is incorrect"}), 400

    if new_password != confirm_password:
        conn.close()
        return jsonify({"ok": False, "error": "New passwords do not match"}), 400

    valid, msg = validate_password(new_password)
    if not valid:
        conn.close()
        return jsonify({"ok": False, "error": msg}), 400

    password_hash = hash_password(new_password)
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user["id"]))
    conn.commit()
    conn.close()

    return jsonify({"ok": True, "message": "Password updated successfully"})


@profile_bp.route("/profile/update", methods=["POST"])
@require_auth
def update_profile():
    user = get_current_user()
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()

    if not name:
        return jsonify({"ok": False, "error": "Name is required"}), 400
    if not email:
        return jsonify({"ok": False, "error": "Email is required"}), 400
    if len(name) < 2 or len(name) > 100:
        return jsonify({"ok": False, "error": "Name must be 2-100 characters"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user["id"]))
    if cursor.fetchone():
        conn.close()
        return jsonify({"ok": False, "error": "Email already in use"}), 400

    cursor.execute(
        "UPDATE users SET name = ?, email = ?, phone = ?, address = ? WHERE id = ?",
        (name, email, phone, address, user["id"])
    )
    conn.commit()
    conn.close()

    return jsonify({"ok": True, "message": "Profile updated successfully"})
