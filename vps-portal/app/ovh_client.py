import ovh
from flask import current_app


def get_client():
    return ovh.Client(
        endpoint=current_app.config["OVH_ENDPOINT"],
        application_key=current_app.config["OVH_APPLICATION_KEY"],
        application_secret=current_app.config["OVH_APPLICATION_SECRET"],
        consumer_key=current_app.config["OVH_CONSUMER_KEY"],
    )


def list_vps():
    client = get_client()
    return client.get("/vps")


def get_vps_info(vps_name):
    client = get_client()
    info = client.get(f"/vps/{vps_name}")
    return info


def get_vps_ips(vps_name):
    client = get_client()
    try:
        ips = client.get(f"/vps/{vps_name}/ips")
        return ips
    except Exception:
        return []


def reboot_vps(vps_name):
    client = get_client()
    return client.post(f"/vps/{vps_name}/reboot")


def list_snapshots(vps_name):
    client = get_client()
    try:
        return client.get(f"/vps/{vps_name}/snapshot")
    except Exception:
        return None


def take_snapshot(vps_name):
    client = get_client()
    return client.post(f"/vps/{vps_name}/createSnapshot")


def get_vps_task(vps_name, task_id):
    client = get_client()
    return client.get(f"/vps/{vps_name}/tasks/{task_id}")
