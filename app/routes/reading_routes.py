from flask import Blueprint, jsonify, request
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
        return output
    except Exception as e:
        return jsonify({"error": str(e)}), 500