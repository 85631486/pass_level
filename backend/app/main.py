import logging
from flask import Flask, jsonify
from flask_cors import CORS

from .api.routes.admin import admin_bp
from .api.routes.auth import auth_bp
from .api.routes.chapters import chapters_bp
from .api.routes.level_maps import level_maps_bp
from .api.routes.levels import levels_bp
from .api.routes.ai_assistant import ai_assistant_bp
from .api.routes.students import students_bp
from .api.routes.tasks import tasks_bp
from .api.routes.task_phases import task_phases_bp
from .api.routes.task_steps import task_steps_bp
from .api.routes.task_phase_question_rel import task_phase_question_rel_bp
from .api.routes.questions import questions_bp
from .core.config import get_settings
from .db.session import close_db, init_db

settings = get_settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["JSON_AS_ASCII"] = False  # Support Chinese characters in JSON

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register database teardown
    app.teardown_appcontext(close_db)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chapters_bp)
    app.register_blueprint(level_maps_bp)
    app.register_blueprint(levels_bp)
    app.register_blueprint(ai_assistant_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(task_phases_bp)
    app.register_blueprint(task_steps_bp)
    app.register_blueprint(task_phase_question_rel_bp)
    app.register_blueprint(questions_bp)

    # Initialize database
    with app.app_context():
        init_db()
        logger.info("Database initialized")

    @app.route("/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"detail": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({"detail": "Internal server error"}), 500

    logger.info("Flask application created")
    return app

