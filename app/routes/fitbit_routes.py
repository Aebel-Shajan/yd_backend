from flask import Blueprint, jsonify, request

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