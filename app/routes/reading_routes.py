from flask import Blueprint, jsonify, request
from app.models import ActivityMetaData, ReadingActivity, ValueColMetaData
from app.routes.utils import get_activities
from app.services.reading_service import handle_kindle_zip

reading_bp = Blueprint("reading",  __name__)

@reading_bp.route("/upload_file", methods=["POST"])
def add_reading_from_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file is None or not file.filename.endswith(".zip"):
        return jsonify({"error": "Invalid file type"}), 400
    
    try:
        output = handle_kindle_zip(file)
        return jsonify(output), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reading_bp.route("/<path:year>", methods=["GET"])
def get_workout_activities(year: str):
    return get_activities(
        year=year,
        model=ReadingActivity,
        metadata=ActivityMetaData(
            date_col="date",
            filter_cols=["asin"],
            value_cols=[
                ValueColMetaData(
                    col="total_reading_minutes",
                    units="minutes"
                )
            ]
        )
    )