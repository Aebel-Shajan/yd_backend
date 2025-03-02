from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.services.workout_service import create_workout
from app.schema.workout import WorkoutSchema

workout_bp = Blueprint("workouts", __name__)

@workout_bp.route("/", methods=["POST"])
def add_workout():
    try:
        # Validate request JSON using Pydantic
        data = WorkoutSchema(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400  # Return validation errors

    # Convert Pydantic model to dictionary
    dict = data.model_dump()
    workout = create_workout(dict)
    return jsonify(workout), 201