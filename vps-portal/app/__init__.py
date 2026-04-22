from flask import Flask
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.auth import auth_bp
    from app.vps import vps_bp
    from app.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(vps_bp)
    app.register_blueprint(main_bp)

    return app
