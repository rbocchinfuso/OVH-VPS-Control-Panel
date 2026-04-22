import os

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
    OVH_ENDPOINT = os.environ.get("OVH_ENDPOINT", "ovh-ca")
    OVH_APPLICATION_KEY = os.environ.get("OVH_APPLICATION_KEY", "")
    OVH_APPLICATION_SECRET = os.environ.get("OVH_APPLICATION_SECRET", "")
    OVH_CONSUMER_KEY = os.environ.get("OVH_CONSUMER_KEY", "")

    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")

    VIEWER_USERNAME = os.environ.get("VIEWER_USERNAME", "viewer")
    VIEWER_PASSWORD_HASH = os.environ.get("VIEWER_PASSWORD_HASH", "")

    PERMANENT_SESSION_LIFETIME = 3600
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
