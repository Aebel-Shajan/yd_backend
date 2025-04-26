from enum import Enum
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
from app.services.retrieve_data import get_data_from_table, get_nth_percentile, get_table_metadata, pascal_to_snake
from app.services.retrieve_data import get_range_for_table_column

router = APIRouter(prefix="/retrieve-data")


models = [
    FitbitCalories,
    FitbitExercise,
    FitbitSleep,
    FitbitSteps,
    KindleReading,
    StrongWorkout
]
ROUTE_MAP = {pascal_to_snake(model.__name__): model for model in models}
route_name_map = {pascal_to_snake(m.__name__): pascal_to_snake(m.__name__) for m in models}
RouteNameEnum = Enum("RouteName", route_name_map)

@router.get("/{data_route}/{year}")
async def get_data_for_source(
    data_route: RouteNameEnum,
    year: int,
):
    data_route = data_route.value
    if data_route not in ROUTE_MAP.keys():
        raise HTTPException(404, f"Route not found. Must be one of {ROUTE_MAP.keys()}")
    
    try:
        with SessionLocal() as db:
            data, metadata = get_data_from_table(
                model=ROUTE_MAP[data_route],
                db=db,
                year=year
            )

            return {
                "status": "success",
                "data": data,
                "metadata": metadata
            }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the file: {str(e)}"
        )


@router.get("/data-routes")
def get_data_routes():
    return {
        "status": "success",
        "data": list(ROUTE_MAP.keys())
    }
    
@router.get("/{data_route}/range/{column}")
def get_range_for_table_column_route(
    data_route: Literal[*ROUTE_MAP.keys()],
    column: str
):
    try:
        with SessionLocal() as db:
            model = ROUTE_MAP[data_route]
            return get_range_for_table_column(model, column,db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the request: {str(e)}"
        )
