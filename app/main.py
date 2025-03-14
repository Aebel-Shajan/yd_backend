from flask import Flask
from app.database import init_db
from app.routes.workout_routes import workout_bp
from app.routes.reading_routes import reading_bp
from app.routes.fitbit_routes import fitbit_bp
from app.routes.github_routes import github_bp
from app.config import Config  # Instead of "config"
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = "super secret key"
    app.config.from_object(Config)  


    init_db()

    app.register_blueprint(workout_bp, url_prefix="/workouts")
    app.register_blueprint(reading_bp, url_prefix="/reading")
    app.register_blueprint(fitbit_bp, url_prefix="/fitbit")
    app.register_blueprint(github_bp, url_prefix="/github")
    

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))