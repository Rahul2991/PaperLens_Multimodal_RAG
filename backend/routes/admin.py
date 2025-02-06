from fastapi import Depends, APIRouter, File, UploadFile
from sqlalchemy.orm import Session
from services.rag_service import get_embed_data_obj, get_vector_db
from models.mongo_db import get_files_collection
from services.admin import create_admin, list_all_users, delete_user_from_db, upload_files
from models.sql_db import get_db
from typing import List
from models.user import User
from auth.dependencies import admin_only
from schemas.user import UserRegister, RegisterResponse

router = APIRouter()

@router.get("/users")
def list_users(db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    return list_all_users(db)

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    """Delete a user (Admin Only)"""
    return delete_user_from_db(db, user_id)

@router.post("/register_admin", response_model=RegisterResponse)
def register(user: UserRegister, db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    new_user = create_admin(user, db)
    return {"message": "New Admin registered successfully", "username": new_user.username}

@router.post("/upload")
async def upload_file(
    files: List[UploadFile] = File(...), 
    tags: str = "",
    current_user: User = Depends(admin_only), 
    files_collection = Depends(get_files_collection),
    embed_data = Depends(get_embed_data_obj),
    vector_db = Depends(get_vector_db)
    ):
    await upload_files(files, tags, files_collection, current_user, embed_data, vector_db)

    return {"message": f"All Files uploaded successfully"}