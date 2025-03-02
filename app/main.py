from flask import Flask
from app.db.database import init_db
from app.routes.workout_routes import workout_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    init_db()

    app.register_blueprint(workout_bp, url_prefix="/workouts")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))