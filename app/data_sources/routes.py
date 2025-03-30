from fastapi import APIRouter
from app.data_sources.google.routes import router as google_router
from app.data_sources.strong.routes import router as strong_router

router = APIRouter(prefix="/data-sources")

router.include_router(google_router)
router.include_router(strong_router)


@router.get("/list-data-sources", )
async def list_data_sources():
    routes = []
    for route in router.routes:
        if hasattr(route, "path") and hasattr(route, "name") and hasattr(route, "methods"):
            if "GET" in route.methods and route.name != "list_data_sources":
                # Remove route parameters from the path
                path = route.path.split("{")[0].rstrip("/")
                routes.append({
                    "path": path,
                    "name": route.name
                })

    return {
        "routes": routes
    }