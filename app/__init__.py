from flask import Flask
from app.extensions import db, migrate, bcrypt, login_manager, limiter
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    return app
