from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
import aiofiles  # Module to deal with files with web app
import logging

from helpers.config import get_settings, settings
from controllers import DataController, ProjectController , ProcessController
from models import ResponseSignal
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes import DataChunk
from models.AssetModel import AssetModel
from models.db_schemes import Asset
from models import AssetTypeEnum

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",    # So now http://localhost:5000/api/v1/ 
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile, 
                      app_settings: settings=Depends(get_settings)):
    project_model = await ProjectModel.create_instance(
        db_client= request.app.db_client
    )

    project = await project_model.get_or_create_project(project_id=project_id)

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
    
    file_path, file_id = data_controller.generate_unique_filepath(
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

    # store asset into db
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )

    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path)
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)


    return JSONResponse(
            content={
            "signal": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
            "file_id": str(asset_record.id),
            }
        )

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client= request.app.db_client
    )

    project = await project_model.get_or_create_project(
        project_id=project_id
    )

    # get asset from db
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    ) 

    # If not file id given get from DB
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=process_request.file_id
        )
        if asset_record is None:
            return JSONResponse(
                content={
                    "signal": ResponseSignal.FILE_ID_ERROR.value
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        project_file_ids = {
            asset_record.id : asset_record.asset_name
        }
    else:
        project_file = await asset_model.get_all_project_assets(
            asset_project_id= project.id,
            asset_type= AssetTypeEnum.FILE.value
        )

        project_file_ids = {
            record.id : record.asset_name
            for record in project_file
        }

    if len(project_file_ids) == 0:
        return JSONResponse(
            content={
                "signal": ResponseSignal.NO_FILES_ERROR.value
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    process_controller = ProcessController(project_id=project_id)
    
    chunk_model = await ChunkModel.create_instance(
            db_client=request.app.db_client
        )

    if do_reset == 1:
        no_deleted = await chunk_model.delete_chunks_by_project_id(project_id=project.id)


    no_records = 0
    no_files = 0

    for asset_id, file_id in project_file_ids.items():
        file_content = process_controller.get_file_content(file_id=file_id)
        
        # If file didn't exsit skip
        if file_content is None:
            logger.error(f"Error while processing file:{file_id}")
            continue

        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )

        if file_chunks is None or len(file_chunks) ==0:
            return JSONResponse(
                content={
                    "signal": ResponseSignal.PROCESSING_FAILED.value
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        file_chunks_record = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_project_id=project.id,
                chunk_asset_id=asset_id
            )
            for i, chunk in enumerate(file_chunks)
        ]

        no_records += await chunk_model.insert_many_chunks(chunks= file_chunks_record)
        no_files += 1

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_file": no_files
        }
    )
