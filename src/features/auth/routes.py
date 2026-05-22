from flask import Blueprint, render_template, request, redirect, make_response

from features.auth.service import (
    verify_password, create_token, get_user_by_email,
    get_user_by_id, create_user, decode_token
)

auth_bp = Blueprint("auth", __name__)


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


@auth_bp.route("/")
def index():
    return redirect("/landing")


@auth_bp.route("/landing")
def landing():
    if get_current_user():
        return redirect("/dashboard")
    error = request.args.get("error", "")
    card = request.args.get("card", "login")
    return render_template("landing.html", error=error, card=card)


@auth_bp.route("/auth/login", methods=["POST"])
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


@auth_bp.route("/auth/register", methods=["POST"])
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


@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    resp = make_response(redirect("/landing"))
    resp.delete_cookie("session")
    return resp
