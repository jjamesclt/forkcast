from flask import Flask
from config import Config
from models import db, User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = "forkcast-dev-key"

    db.init_app(app)

    with app.app_context():
        db.create_all()
        _seed_users(app.config.get("USER_LIST", Config.USER_LIST))

    # Register blueprints
    from routes.main import main_bp
    from routes.meals import meals_bp
    from routes.sessions import sessions_bp
    from routes.history import history_bp
    from routes.settings import settings_bp
    from routes.llm import llm_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(meals_bp, url_prefix="/meals")
    app.register_blueprint(sessions_bp, url_prefix="/sessions")
    app.register_blueprint(history_bp, url_prefix="/history")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(llm_bp, url_prefix="/llm")

    return app


def _seed_users(user_list):
    """Create users from USER_LIST env if they don't exist."""
    if not user_list:
        return
    for name in user_list:
        existing = User.query.filter_by(name=name).first()
        if not existing:
            db.session.add(User(name=name, active=True))
    db.session.commit()


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=Config.HTTP_PORT, debug=True)
