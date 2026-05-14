from flask import Flask

def create_app():
    app = Flask(__name__)

    # extensions
    from app.extensions import db, migrate, bcrypt, login_manager, limiter

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # blueprints (safe import)
    try:
        from app.routes import bp as main_bp
        app.register_blueprint(main_bp)
    except Exception:
        pass

    return app
