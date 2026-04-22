from functools import wraps

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("auth.login", next=request.path))
        if session.get("role") != "admin":
            flash("You do not have permission to perform this action.", "danger")
            return redirect(url_for("vps.index"))
        return f(*args, **kwargs)
    return decorated


def _check_credentials(username, password):
    cfg = current_app.config

    if username == cfg["ADMIN_USERNAME"] and cfg["ADMIN_PASSWORD_HASH"]:
        if check_password_hash(cfg["ADMIN_PASSWORD_HASH"], password):
            return "admin"

    if username == cfg["VIEWER_USERNAME"] and cfg["VIEWER_PASSWORD_HASH"]:
        if check_password_hash(cfg["VIEWER_PASSWORD_HASH"], password):
            return "viewer"

    return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("vps.index"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = _check_credentials(username, password)
        if role:
            session.permanent = True
            session["username"] = username
            session["role"] = role
            next_url = request.args.get("next") or url_for("vps.index")
            return redirect(next_url)
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
