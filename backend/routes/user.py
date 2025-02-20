from fastapi import APIRouter, Depends, File, UploadFile, Form
from auth.dependencies import verify_token
from models.mongo_db import get_files_collection
from motor.motor_asyncio import AsyncIOMotorCollection
from rag_modules.embed_data import EmbedData
from rag_modules.vector_db import QdrantVDB
from models.user import User
from services.rag_service import get_embed_data_obj, get_vector_db
from services.user import list_all_files, upload_files
from typing import List
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

# Create a FastAPI router for user-related endpoints
router = APIRouter()

@router.post("/upload")
async def upload_file(
    files: List[UploadFile] = File(...), 
    tags: str = Form(...),
    current_user: User = Depends(verify_token), 
    files_collection: AsyncIOMotorCollection = Depends(get_files_collection),
    embed_data: EmbedData = Depends(get_embed_data_obj),
    vector_db: QdrantVDB = Depends(get_vector_db)
    ):
    """
    Handles file uploads, stores metadata in the database, and processes embeddings and store in vector db.

    Args:
        files (List[UploadFile]): List of files uploaded by the user.
        tags (str): Tags associated with the uploaded files.
        current_user (User): The authenticated user uploading the files.
        files_collection: MongoDB collection for file metadata storage.
        embed_data: Embedding model instance for processing file data.
        vector_db: Vector database instance for storing and retrieving embeddings.

    Returns:
        dict: A message indicating success or failure to upload.
    """
    
    logger.info(f"User {current_user.username} is uploading {len(files)} file(s) with tags: {tags}")
    
    # Process and upload files
    await upload_files(files, tags, files_collection, current_user, embed_data, vector_db)

    logger.info(f"Files uploaded successfully for user: {current_user.username}")
    
    return {"message": f"All Files uploaded successfully"}

@router.get("/list_files")
async def list_files(current_user: User = Depends(verify_token), files_collection: AsyncIOMotorCollection = Depends(get_files_collection)):
    """
    Retrieves the list of files uploaded by the authenticated user.

    Args:
        current_user (User): The authenticated user making the request.
        files_collection: MongoDB collection for file metadata storage.

    Returns:
        List[dict]: A list of file metadata stored in the database.
    """
    
    logger.info(f"Fetching file list for user: {current_user.username}")
    
    file_list = await list_all_files(current_user, files_collection)

    logger.info(f"Retrieved {len(file_list)} file(s) for user: {current_user.username}")

    return file_list