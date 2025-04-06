from typing_extensions import Literal
from fastapi import APIRouter, HTTPException
from app.database.session import SessionLocal
from app.data_sources.services import get_data_from_table
from app.data_sources.google.fitbit.models import (
    FitbitCalories,
    FitbitExercise,
    FitbitSleep,
    FitbitSteps
)


router = APIRouter(prefix="/fitbit")

ROUTE_MAP = {
    "calories":    FitbitCalories, 
    "steps":    FitbitSteps,
    "sleep":     FitbitSleep,
    "exercises" :   FitbitExercise,
}
routes = list(ROUTE_MAP.keys())

@router.get("/{data_route}/{year}")
async def get_fitbit_data(
    data_route: Literal[*routes],
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
    


    raise HTTPException(400, detail="Data file for data source not found!")


