from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    # Use DATABASE_URL from Render if available (PostgreSQL)
    db_url = os.environ.get("DATABASE_URL")

    # Render gives URLs starting with postgres:// (old), SQLAlchemy needs postgresql://
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    if db_url:
        # Running on Render → use Postgres
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    else:
        # Running locally → use SQLite
        db_path = os.path.join(app.instance_path, "notes.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    app.secret_key = 'goated_key'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    Migrate(app, db)

    from routes import register_routes
    register_routes(app, db)

      # Auto-migrate on startup
    with app.app_context():
        try:
            from alembic import command
            from alembic.config import Config

            alembic_cfg = Config("migrations/alembic.ini")
            command.upgrade(alembic_cfg, "head")
        except Exception as e:
            print("Migration failed:", e)

    return app

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
