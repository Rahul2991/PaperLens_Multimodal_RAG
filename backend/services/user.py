from fastapi import HTTPException, UploadFile, status
from rag_modules.document_extract import extract_image_data, extract_pdf_data, extract_txt_data
from rag_modules.embed_data import EmbedData
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List
from rag_modules.vector_db import QdrantVDB
from utils import get_file_hash, get_unique_filename, is_image, is_pdf, is_txt
from services.rag_service import bot
from datetime import datetime
from models.user import User
from pathlib import Path
from config import Config
import os

UPLOAD_FOLDER = Path(Config.USER_UPLOAD_FILE_LOCATION)

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
                
                user_folder_name = current_user.username + '_' + str(current_user.id)
                
                BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                os.makedirs(os.path.join(BASE_DIR, UPLOAD_FOLDER, user_folder_name), exist_ok=True)
                
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
                    "collection_name": collection_name,
                    "tags": tags
                }
                
                await files_collection.insert_one(metadata)
            except Exception as e:
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise
        return {"message": f"File uploaded successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )
        
async def list_all_files(current_user: User, files_collection: AsyncIOMotorCollection):
    try:
        files_list = await files_collection.find().to_list()
        return [{"id": str(file['_id']),
                "filename": file['filename'],
                "upload_time": file['upload_time'].strftime("%Y-%m-%d %H:%M:%S"),
                "tags": file['tags']} for file in files_list if current_user.username == file['uploader']]
    except Exception as e:
        print(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch files info : {str(e)}"
        )