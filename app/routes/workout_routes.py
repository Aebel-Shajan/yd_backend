import os
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.models import WorkoutActivity
from app.services.utils import add_activity_to_db
from app.services.workout_service import process_strong_csv
from app.config import Config

workout_bp = Blueprint("workouts", __name__)

@workout_bp.route("/", methods=["POST"])
def add_workout():
    try:
        data = WorkoutActivity(**request.json)
        workout = add_activity_to_db(data, WorkoutActivity)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400  # Return validation errors
    except ValueError as e:
        return jsonify({"error": str(e)})
    
    return jsonify(workout), 201

@workout_bp.route("/upload_file", methods=["POST"])
def add_workouts_from_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file and Config.allowed_file(file.filename):
        save_path = os.path.join(Config.UPLOAD_FOLDER, file.filename)
        file.save(save_path)
        with open(save_path) as file:
            output = process_strong_csv(file)

        return jsonify(output), 201
    
    return jsonify({"error": "Invalid file type"}), 400
