from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os
import aiofiles  # Module to deal with files with web app
import logging

from helpers.config import get_settings, settings
from controllers import DataController, ProjectController
from models import ResponseSignal

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",    # So now http://localhost:5000/api/v1/ 
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile, 
                      app_settings: settings=Depends(get_settings)):
    
    # Validate the file propertires
    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
                content={
                "signal": result_signal
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
    
    file_path = data_controller.generate_unique_filename(
        orig_file_name=file.filename,
        project_id=project_id
    )

    # Save file chunk by chunk instead of wait untill the whole
    #  file uploaded then download it
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        
        logger.error(f"Error while uploading file: {e}")
        
        return JSONResponse(
                content={
                "signal": ResponseSignal.FILE_UPLOADED_FAILED.value
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            ) 
        
    return JSONResponse(
            content={
            "signal": ResponseSignal.FILE_UPLOADED_SUCCESS.value
            }
        )   