from flask import Flask
from dotenv import load_dotenv
import os

from shared.db import init_db

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "default-secret-key-change-me")

    from features.auth.routes import auth_bp
    from features.expenses.routes import expenses_bp
    from features.profile.routes import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(profile_bp)

    return app


if __name__ == "__main__":
    init_db()
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
