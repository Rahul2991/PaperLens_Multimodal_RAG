from fastapi import Depends, APIRouter, File, UploadFile, Form
from sqlalchemy.orm import Session
from services.rag_service import get_embed_data_obj, get_vector_db
from models.mongo_db import get_files_collection
from services.admin import create_admin, list_all_users, delete_user_from_db, upload_files, list_all_files
from models.sql_db import get_db
from typing import List
from models.user import User
from auth.dependencies import admin_only
from schemas.user import UserRegister, RegisterResponse
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

# Create a FastAPI router for admin-related endpoints
router = APIRouter()

@router.get("/users")
def list_users(db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    """
    Retrieve a list of all registered users. (Admin Only)
    
    Args:
        - db: Database session dependency
        - current_user: The currently authenticated admin user

    Returns:
        - List of user details
    """
    logger.info(f"Admin {current_user.username} requested the list of all users.")
    return list_all_users(db)

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    """
    Delete a user by user ID. (Admin Only)
    
    Args:
        - user_id: ID of the user to be deleted
        - db: Database session dependency
        - current_user: The currently authenticated admin user

    Returns:
        - Confirmation message upon successful deletion
    """
    logger.info(f"Admin {current_user.username} is deleting user with ID {user_id}.")
    return delete_user_from_db(db, user_id)

@router.post("/register_admin", response_model=RegisterResponse)
def register(user: UserRegister, db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    """
    Register a new admin user. (Admin Only)
    
    Args:
        - user: Admin user registration details
        - db: Database session dependency
        - current_user: The currently authenticated admin user

    Returns:
        - Confirmation message and username of the newly created admin
    """
    logger.info(f"Admin {current_user.username} is registering a new admin: {user.username}.")
    new_user = create_admin(user, db)
    return {"message": "New Admin registered successfully", "username": new_user.username}

@router.post("/upload")
async def upload_file(
    files: List[UploadFile] = File(...), 
    tags: str = Form(...),
    current_user: User = Depends(admin_only), 
    files_collection = Depends(get_files_collection),
    embed_data = Depends(get_embed_data_obj),
    vector_db = Depends(get_vector_db)
    ):
    """
    Upload files to the system with associated tags. (Admin Only)
    
    Args:
        - files: List of files to be uploaded
        - tags: Tags associated with the files
        - current_user: The currently authenticated admin user
        - files_collection: MongoDB collection dependency
        - embed_data: Dependency for embedding data
        - vector_db: Dependency for vector database operations

    Returns:
        - Confirmation message upon successful file upload
    """
    logger.info(f"Admin {current_user.username} is uploading {len(files)} files with tags: {tags}.")
    await upload_files(files, tags, files_collection, current_user, embed_data, vector_db)

    return {"message": f"All Files uploaded successfully"}

@router.get("/list_files")
async def list_files(current_user: User = Depends(admin_only), files_collection = Depends(get_files_collection),):
    """
    Retrieve a list of all uploaded files. (Admin Only)
    
    Args:
        - current_user: The currently authenticated admin user
        - files_collection: MongoDB collection dependency

    Returns:
        - List of all files in the system
    """
    logger.info(f"Admin {current_user.username} requested the list of all files.")
    return await list_all_files(files_collection)