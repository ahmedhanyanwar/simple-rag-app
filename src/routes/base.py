from fastapi import FastAPI, APIRouter
import os

base_router = APIRouter(
    prefix="/api/v1",    # So now http://localhost:5000/api/v1/ 
    tags=["api_v1"],
)

@base_router.get("/") # default route
async def wolcome():
    app_name = os.getenv('APP_NAME')
    app_version = os.getenv('APP_VERSION')

    return {
        "app_name": app_name,
        "app_version": app_version,
    }