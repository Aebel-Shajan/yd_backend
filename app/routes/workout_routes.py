import os
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.models import ActivityMetaData, ValueColMetaData, WorkoutActivity
from app.routes.utils import get_activities
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
def get_workout_activities(year: str):
    return get_activities(
        year=year,
        model=WorkoutActivity,
        metadata=ActivityMetaData(
            date_col="date",
            filter_cols=["workout_name", "exercise_name"],
            value_cols=[
                ValueColMetaData(
                    col="total_volume",
                    units="kg"
                ),
                ValueColMetaData(
                    col="workout_duration_minutes",
                    units="minutes"
                )
            ]
        )
    )