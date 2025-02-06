from auth.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException, UploadFile, status
from rag_modules.document_extract import extract_image_data, extract_pdf_data, extract_txt_data
from rag_modules.embed_data import EmbedData
from rag_modules.vector_db import QdrantVDB
from utils import get_file_hash, get_unique_filename, is_image, is_pdf, is_txt
from schemas.user import UserRegister, UserLogin
from services.rag_service import bot
from datetime import datetime
from sqlalchemy.orm import Session
from models.user import User
from pathlib import Path
from config import Config
import os

UPLOAD_FOLDER = Path(Config.USER_UPLOAD_FILE_LOCATION)

def create_user(user: UserRegister, db: Session) -> User:
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    hashed_pw = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    return new_user

def authenticate_user(user: UserLogin, db: Session):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return db_user

def create_access_token_for_user(user: UserLogin) -> str:
    return create_access_token(data={"sub": user.username})

async def upload_file(file: UploadFile, files_collection, current_user: User, embed_data: EmbedData, vector_db: QdrantVDB):
    try:
        file_bytes = await file.read()
        file_hash = get_file_hash(file_bytes)
        
        existing_file = await files_collection.find_one({"file_hash": file_hash})
        
        if existing_file:
            return {"message": f"File already exists"}
        
        unique_filename = get_unique_filename(file.filename)
        
        user_folder_name = current_user.username + '_' + current_user.id
        
        os.makedirs(os.path.join(UPLOAD_FOLDER, user_folder_name), exist_ok=True)
        
        file_path = os.path.join(UPLOAD_FOLDER, user_folder_name, unique_filename)
    
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
            
        collection_name = 'multimodal_rag_' + user_folder_name
        vector_db.create_or_set_collection(collection_name)
        vector_db.ingest_data(embed_data, source=file_path)
        
        metadata = {
            "filename": file.filename,
            "unique_filename": unique_filename,
            "file_hash": file_hash,
            "uploader": current_user.username,
            "uploader_role": 'user',
            "upload_time": datetime.now(),
            "file_path": str(file_path),
            "collection_name": collection_name
        }
        
        await files_collection.insert_one(metadata)
        
        return {"message": f"File uploaded successfully"}
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )