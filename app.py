from flask import Flask, render_template, redirect, request, make_response, jsonify
from datetime import datetime
from typing import Optional

from Database.db import init_db, seed_db, get_db, CATEGORIES
from Database.auth import (
    verify_password,
    create_token,
    decode_token,
    create_user,
    get_user_by_email,
    get_user_by_id,
)


STANDARD_EXPIRE = 86400
REMEMBER_ME_EXPIRE = 604800



app = Flask(__name__)

with app.app_context():
    init_db()
    seed_db()


def get_current_user(session: Optional[str] = None) -> Optional[dict]:
    if not session:
        return None
    payload = decode_token(session)
    if not payload:
        return None
    user_id = payload.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


def get_session_from_request():
    return request.cookies.get("session")


@app.route("/")
def home():
    return redirect("/landing")


@app.route("/landing")
def landing():
    error = request.args.get("error", "")
    card = request.args.get("card", "login")
    return render_template("landing.html", error=error, card=card)


@app.route("/dashboard")
def dashboard():
    session = get_session_from_request()
    user = get_current_user(session)

    if not user:
        return redirect("/landing?error=Please+log+in+to+view+your+dashboard&card=login")

    user_id = user["id"]
    month = request.args.get("month")

    conn = get_db()
    cursor = conn.cursor()

    if month:
        year, month_num = month.split("-")
        cursor.execute("""
            SELECT id, category, amount, date, description, created_at
            FROM expenses
            WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
            ORDER BY date DESC, created_at DESC
        """, (user_id, year, month_num))
    else:
        cursor.execute("""
            SELECT id, category, amount, date, description, created_at
            FROM expenses
            WHERE user_id = ?
            ORDER BY date DESC, created_at DESC
        """, (user_id,))

    expenses = cursor.fetchall()
    conn.close()

    data = [
        (
            exp["category"],
            exp["amount"],
            exp["date"],
            exp["description"] or "",
            exp["created_at"],
            exp["id"]
        )
        for exp in expenses
    ]

    total_expenses = round(sum(exp[1] for exp in data), 2)
    now = datetime.now()
    month_year = month or f"{now.year}-{now.month:02d}"

    return render_template("index.html",
        data=data,
        total_expenses=total_expenses,
        month_year=month_year,
        categories=CATEGORIES,
    )


@app.route("/add", methods=["POST"])
def add_expense():
    session = get_session_from_request()
    user = get_current_user(session)

    if not user:
        return redirect("/landing?error=Please+log+in+to+add+expenses&card=login")

    user_id = user["id"]
    name = request.form.get("name", "")
    price = request.form.get("price", type=float, default=0)
    description = request.form.get("description")

    if price <= 0:
        return redirect("/dashboard?error=Amount+must+be+greater+than+0")
    if name not in CATEGORIES:
        return redirect("/dashboard?error=Invalid+category")
    if description and len(description) > 500:
        return redirect("/dashboard?error=Description+too+long")

    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        (user_id, price, name, today, description)
    )
    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/remove", methods=["POST"])
def remove_expenses():
    session = get_session_from_request()
    user = get_current_user(session)

    if not user:
        return redirect("/landing?error=Please+log+in&card=login")

    user_id = user["id"]
    items = request.form.getlist("items")

    if items:
        conn = get_db()
        cursor = conn.cursor()
        for item in items:
            parts = item.split(",")
            if len(parts) >= 3:
                category = parts[0]
                amount = float(parts[1])
                date = parts[2]
                cursor.execute(
                    """DELETE FROM expenses
                       WHERE user_id = ? AND category = ? AND amount = ? AND date = ?
                       LIMIT 1""",
                    (user_id, category, amount, date)
                )
        conn.commit()
        conn.close()

    return redirect("/dashboard")


@app.route("/auth/login", methods=["POST"])
def login():
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    remember_me = request.form.get("remember_me", "")

    user = get_user_by_email(email)

    if not user or not verify_password(password, user["password_hash"]):
        response = make_response(redirect("/landing?error=Email+or+password+does+not+match&card=login"))
        return response

    token = create_token(user["id"])
    max_age = REMEMBER_ME_EXPIRE if remember_me == "on" else STANDARD_EXPIRE

    response = make_response(redirect("/dashboard"))
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=max_age,
    )
    return response


@app.route("/auth/register", methods=["POST"])
def register():
    name = request.form.get("name", "")
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if password != confirm_password:
        return redirect("/landing?error=Passwords+do+not+match&card=register")

    success, error_msg = create_user(name, email, password)

    if not success:
        return redirect(f"/landing?error={error_msg.replace(' ', '+')}&card=register")

    user = get_user_by_email(email)
    token = create_token(user["id"])

    response = make_response(redirect("/dashboard"))
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=STANDARD_EXPIRE,
    )
    return response


@app.route("/auth/logout", methods=["POST"])
def logout():
    response = make_response(redirect("/landing"))
    response.delete_cookie(key="session")
    return response


@app.route("/get-user", methods=["GET"])
def get_user():
    session = get_session_from_request()
    user = get_current_user(session)

    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    return jsonify({
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)