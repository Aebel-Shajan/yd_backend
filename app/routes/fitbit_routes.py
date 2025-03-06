from flask import Blueprint, jsonify, request

from app.models import ActivityMetaData, CalorieActivity, ExerciseActivity, SleepActivity, StepActivity, ValueColMetaData
from app.routes.utils import get_activities
from app.services.fitbit_service import handle_fitbit_zip

fitbit_bp = Blueprint("fitbit", __name__)

@fitbit_bp.route("/upload_file", methods=["POST"])
def add_fitbit_data_from_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file is None or not file.filename.endswith(".zip"):
        return jsonify({"error": "Invalid file type"}), 400
    
    try:
        output = handle_fitbit_zip(file)
        return output
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@fitbit_bp.route("/calories/<path:year>", methods=["GET"])
def get_calories_activities(year: str):
    metadata=ActivityMetaData(
        date_col="date",
        value_cols=[
            ValueColMetaData(
                col="value",
                units="calories"
            )
        ],
        filter_cols=[],
    )
    return get_activities(
        year=year,
        model=CalorieActivity,
        metadata=metadata
    )
    
@fitbit_bp.route("/steps/<path:year>", methods=["GET"])
def get_step_activities(year: str):
    metadata=ActivityMetaData(
        date_col="date",
        value_cols=[
            ValueColMetaData(
                col="value",
                units="steps"
            )
        ],
        filter_cols=[],
    )
    return get_activities(
        year=year,
        model=StepActivity,
        metadata=metadata
    )
    
@fitbit_bp.route("/exercise/<path:year>", methods=["GET"])
def get_exercise_activities(year: str):
    metadata=ActivityMetaData(
        date_col="date",
        value_cols=[
            ValueColMetaData(
                col="active_duration",
                units="milliseconds"
            ),
            ValueColMetaData(
                col="average_heart_rate",
                units="bpm"
            ),
            ValueColMetaData(
                col="calories",
                units="calores"
            )
        ],
        filter_cols=["activity_name"],
    )
    return get_activities(
        year=year,
        model=ExerciseActivity,
        metadata=metadata
    )
    
@fitbit_bp.route("/sleep/<path:year>", methods=["GET"])
def get_sleep_activities(year: str):
    metadata=ActivityMetaData(
        date_col="date",
        value_cols=[
            ValueColMetaData(
                col="total_duration_hours",
                units="hours"
            )
        ],
        filter_cols=[],
    )
    return get_activities(
        year=year,
        model=SleepActivity,
        metadata=metadata
    )
    
