from fastapi import HTTPException, UploadFile, status, File
from rag_modules.vector_db import QdrantVDB
from rag_modules.embed_data import EmbedData
from rag_modules.document_extract import extract_pdf_data, extract_txt_data, extract_image_data
from services.rag_service import bot
from typing import List
from utils import get_file_hash, get_unique_filename, is_image, is_pdf, is_txt
from datetime import datetime
from models.user import User
from sqlalchemy.orm import Session
from schemas.user import UserRegister
from auth.security import hash_password
from pathlib import Path
from config import Config
from motor.motor_asyncio import AsyncIOMotorCollection
import os

UPLOAD_FOLDER = Path(Config.ADMIN_UPLOAD_FILE_LOCATION)

def list_all_users(db: Session):
    users_list = db.query(User).all()
    return [user.to_dict() for user in users_list]

def delete_user_from_db(db: Session, user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.username} deleted successfully"}

def create_admin(user: UserRegister, db: Session) -> User:
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    hashed_pw = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw, is_admin=True)
    db.add(new_user)
    db.commit()
    return new_user

async def upload_files(files: List[UploadFile], tags: str, files_collection: AsyncIOMotorCollection, current_user: User, embed_data: EmbedData, vector_db: QdrantVDB):
    try:
        for file in files:
            try:
                file_bytes = await file.read()
                file_hash = get_file_hash(file_bytes)
                
                existing_file = await files_collection.find_one({"file_hash": file_hash})
                
                if existing_file: continue
                    # return {"message": f"File already exists"}
                
                unique_filename = get_unique_filename(file.filename)
                
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
                with open(file_path, "wb") as buffer:
                    buffer.write(file_bytes)
                    
                if await is_pdf(file_bytes):
                    extracted_data = extract_pdf_data(file_path=file_path, bot=bot)
                    if extracted_data:
                        texts, image_summaries, table_summaries = extracted_data
                        embed_data.embed(texts + image_summaries + table_summaries)
                    else:
                        raise Exception("Failed to fetch extract data.")
                elif await is_txt(file_bytes):
                    extracted_data = extract_txt_data(file_path=file_path)
                    if extracted_data:
                        texts = extracted_data
                        embed_data.embed(texts)
                    else:
                        raise Exception("Failed to fetch extract data.")
                elif await is_image(file_bytes):
                    extracted_data = extract_image_data(file_path=file_path, bot=bot)
                    if extracted_data:
                        image_summaries = extracted_data
                        embed_data.embed(image_summaries)
                    else:
                        raise Exception("Failed to fetch extract data.")
                    
                collection_name = 'multimodal_rag_admin_collection'
                vector_db.create_or_set_collection(collection_name)
                vector_db.ingest_data(embed_data, source=file_path)
                
                metadata = {
                    "filename": file.filename,
                    "unique_filename": unique_filename,
                    "file_hash": file_hash,
                    "uploader": current_user.username,
                    "uploader_role": 'admin',
                    "upload_time": datetime.now(),
                    "file_path": str(file_path),
                    "collection_name": collection_name,
                    "tags": tags
                }
                
                await files_collection.insert_one(metadata)
            except Exception as e:
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise
        return {"message": f"Files uploaded successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

async def list_all_files(db: Session, current_user: User, files_collection: AsyncIOMotorCollection):
    try:
        files_list = await files_collection.find().to_list()
        return [{"id": str(file['_id']),
                "filename": file['filename'],
                "uploader": file['uploader'],
                "role": file['uploader_role'],
                "upload_time": file['upload_time'].strftime("%Y-%m-%d %H:%M:%S"),
                "collection_name": file['collection_name'],
                "tags": file['tags']} for file in files_list]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch files info : {str(e)}"
        )