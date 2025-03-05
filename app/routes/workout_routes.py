import os
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.models import WorkoutActivity
from app.services.utils import add_activity_to_db, selct_activities_from_db
from app.services.workout_service import handle_strong_csv
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
    
    if file is None or not file.filename.endswith(".csv"):
        return jsonify({"error": "Invalid file type"}), 400
    
    try:
        save_path = os.path.join(Config.UPLOAD_FOLDER, file.filename)
        file.save(save_path)
        
        with open(save_path) as file:
            output = handle_strong_csv(file)
            return jsonify(output), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@workout_bp.route("/get_activities/<path:year>", methods=["GET"])
def get_workout_activites(year: str):
    if year is None:
        return jsonify({"error": "Error expected year query parameter."}), 400
    
    year: int = int(year)
    try:
        activities = selct_activities_from_db(WorkoutActivity, year)
        return jsonify(
            {
                "data": activities,
                "metadata": {
                    "filter_cols": [
                        "workout_name",
                        "exercise_name"
                    ],
                    "value_cols":[
                        {
                            "col": "total_volume",
                            "unit": "kg"
                        },
                        {
                            "col": "workout_duration_minutes",
                            "units": "minutes"
                        }
                    ],
                    "date_col": "date"
                }
            }
        ), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500