
from flask import jsonify
from sqlmodel import SQLModel

from app.models import ActivityMetaData
from app.services.utils import selct_activities_from_db


def get_activities(year: str, model: type[SQLModel], metadata: ActivityMetaData):
    if year is None:
        return jsonify({"error": "Error expected year query parameter."}), 400
    
    year: int = int(year)
    try:
        activities = selct_activities_from_db(model, year)
        return jsonify(
            {
                "data": activities,
                "metadata": metadata.model_dump()
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500