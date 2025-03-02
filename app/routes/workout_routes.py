from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.services.workout_service import create_workout
from app.services.utils import check_duplicate
from app.schema.workout import WorkoutSchema

workout_bp = Blueprint("workouts", __name__)

@workout_bp.route("/", methods=["POST"])
def add_workout():
    try:
        data = WorkoutSchema(**request.json)
        workout = create_workout(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400  # Return validation errors
    except ValueError as e:
        return jsonify({"error": str(e)})
    
    return jsonify(workout), 201