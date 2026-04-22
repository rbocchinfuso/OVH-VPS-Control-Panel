from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.auth import admin_required, login_required
from app import ovh_client

vps_bp = Blueprint("vps", __name__, url_prefix="/vps")


@vps_bp.route("/")
@login_required
def index():
    error = None
    instances = []
    try:
        names = ovh_client.list_vps()
        for name in names:
            try:
                info = ovh_client.get_vps_info(name)
                ips = ovh_client.get_vps_ips(name)
                instances.append({
                    "name": name,
                    "state": info.get("state", "unknown"),
                    "displayName": info.get("displayName", name),
                    "offer": info.get("offerType", ""),
                    "zone": info.get("zone", ""),
                    "ips": ips,
                    "ram": info.get("ram", {}).get("size", ""),
                    "vcore": info.get("vcore", ""),
                    "disk": info.get("disk", [{}])[0].get("size", "") if info.get("disk") else "",
                })
            except Exception as e:
                instances.append({"name": name, "state": "error", "displayName": name, "error": str(e)})
    except Exception as e:
        error = f"Failed to connect to OVH API: {e}"

    return render_template(
        "vps/index.html",
        instances=instances,
        error=error,
        role=session.get("role"),
    )


@vps_bp.route("/<vps_name>")
@login_required
def detail(vps_name):
    try:
        info = ovh_client.get_vps_info(vps_name)
        ips = ovh_client.get_vps_ips(vps_name)
        snapshot = ovh_client.list_snapshots(vps_name)
    except Exception as e:
        flash(f"Failed to load VPS details: {e}", "danger")
        return redirect(url_for("vps.index"))

    return render_template(
        "vps/detail.html",
        vps=info,
        vps_name=vps_name,
        ips=ips,
        snapshot=snapshot,
        role=session.get("role"),
    )


@vps_bp.route("/<vps_name>/reboot", methods=["POST"])
@admin_required
def reboot(vps_name):
    try:
        result = ovh_client.reboot_vps(vps_name)
        flash(f"Reboot initiated for {vps_name} (task {result.get('id', 'N/A')}).", "success")
    except Exception as e:
        flash(f"Reboot failed: {e}", "danger")
    return redirect(url_for("vps.detail", vps_name=vps_name))


@vps_bp.route("/<vps_name>/snapshot", methods=["POST"])
@admin_required
def snapshot(vps_name):
    try:
        result = ovh_client.take_snapshot(vps_name)
        flash(f"Snapshot started for {vps_name} (task {result.get('id', 'N/A')}).", "success")
    except Exception as e:
        flash(f"Snapshot failed: {e}", "danger")
    return redirect(url_for("vps.detail", vps_name=vps_name))
