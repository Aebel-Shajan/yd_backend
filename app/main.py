from flask import Flask, jsonify, request, session
from flask_cors import CORS
from app.database import init_db
from app.routes.workout_routes import workout_bp
from app.routes.reading_routes import reading_bp
from app.routes.fitbit_routes import fitbit_bp
from app.routes.github_routes import github_bp
from app.config import Config  # Instead of "config"
import os


app = Flask(__name__)
app.secret_key = "super secret key"
app.config.from_object(Config)
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
  
CORS(
    app=app, 
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "https://year-in-data.vercel.app",
            ]
        }
    },
    supports_credentials=True
)

init_db()

app.register_blueprint(workout_bp, url_prefix="/workouts")
app.register_blueprint(reading_bp, url_prefix="/reading")
app.register_blueprint(fitbit_bp, url_prefix="/fitbit")
app.register_blueprint(github_bp, url_prefix="/github")

@app.before_request
def check_github_auth():
    """Ensure authenticated with github and username is correct."""
    if request.method == "POST":
        try:
            token = session["github_token"]
            username = session["github_username"]
        except KeyError:
            return "error: Authenticate as Aebel-Shajan with github first before making post calls!", 400
    
        if username != "Aebel-Shajan":
            return "error: Only github user Aebel-Shajan can POST to this api!", 400


@app.route("/", methods=["GET"])
def home():
    routes = []
    for rule in app.url_map.iter_rules():
        if "static" in rule.endpoint:  # Skip static files
            continue
        routes.append({
            "route": str(rule),
            "methods": list(rule.methods - {"OPTIONS", "HEAD"})  # Remove unwanted methods
        })
    return jsonify(routes), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))