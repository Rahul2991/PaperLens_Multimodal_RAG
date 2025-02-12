from fastapi import APIRouter, Depends, File, UploadFile, Form
from auth.dependencies import verify_token
from models.mongo_db import get_files_collection
from models.user import User
from services.rag_service import get_embed_data_obj, get_vector_db
from services.user import list_all_files, upload_files
from typing import List

router = APIRouter()

@router.post("/upload")
async def upload_file(
    files: List[UploadFile] = File(...), 
    tags: str = Form(...),
    current_user: User = Depends(verify_token), 
    files_collection = Depends(get_files_collection),
    embed_data = Depends(get_embed_data_obj),
    vector_db = Depends(get_vector_db)
    ):
    await upload_files(files, tags, files_collection, current_user, embed_data, vector_db)

    return {"message": f"All Files uploaded successfully"}

@router.get("/list_files")
async def list_files(current_user: User = Depends(verify_token), files_collection = Depends(get_files_collection),):
    return await list_all_files(current_user, files_collection)