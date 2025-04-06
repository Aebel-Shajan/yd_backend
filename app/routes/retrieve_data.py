

from typing import Literal
from fastapi import APIRouter, HTTPException
from app.database.session import SessionLocal
from app.models.fibit import (
    FitbitCalories,
    FitbitExercise,
    FitbitSleep,
    FitbitSteps
)
from app.models.kindle import KindleReading
from app.models.strong import StrongWorkout
from app.services.retrieve_data import get_data_from_table, pascal_to_snake

router = APIRouter(prefix="/retrieve_data")


models = [
    FitbitCalories,
    FitbitExercise,
    FitbitSleep,
    FitbitSteps,
    KindleReading,
    StrongWorkout
]
ROUTE_MAP = {pascal_to_snake(model.__name__): model for model in models}

@router.get("/{data_route}/{year}")
async def get_fitbit_data(
    data_route: Literal[*ROUTE_MAP.keys()], # type: ignore
    year: int,
):

    if data_route not in ROUTE_MAP.keys():
        raise HTTPException(404, "Route not found. Must be one of {allowed_routes}")
    
    with SessionLocal() as db:
        data, metadata = get_data_from_table(
            model=ROUTE_MAP[data_route],
            db=db,
            year=year
        )

        if data:
            return {
                "status": "success",
                "data": data,
                "metadata": metadata
            }

    raise HTTPException(400, detail="Could not find data for data source!")



