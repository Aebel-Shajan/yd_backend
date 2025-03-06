from flask import Blueprint, jsonify, request

from app.models import ActivityMetaData, CalorieActivity, ValueColMetaData
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