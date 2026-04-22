from flask import Blueprint, redirect, url_for

from app.auth import login_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    return redirect(url_for("vps.index"))


@main_bp.route("/health")
def health():
    return {"status": "ok"}, 200
