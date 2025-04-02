from fastapi import APIRouter, Depends
from helpers.config import get_settings, settings

base_router = APIRouter(
    prefix="/api/v1",    # So now http://localhost:5000/api/v1/ 
    tags=["api_v1"],
)

@base_router.get("/") # default route
async def wolcome(app_settings: settings=Depends(get_settings)):

    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION

    return {
        "app_name": app_name,
        "app_version": app_version,
    }