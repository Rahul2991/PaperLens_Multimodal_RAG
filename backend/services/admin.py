from fastapi import HTTPException, UploadFile, status
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
import os, logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

# Define the upload folder path from configuration
UPLOAD_FOLDER = Path(Config.ADMIN_UPLOAD_FILE_LOCATION)

def list_all_users(db: Session):
    """
    Lists all users in the database.

    Args:
        db: The database session object.

    Returns:
        A list of dictionaries representing all users in the database.
    """
    try:
        # Fetch all users from the database
        users_list = db.query(User).all()
        return [user.to_dict() for user in users_list]
    except Exception as e:
        logger.error(f"Failed to list users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )

def delete_user_from_db(db: Session, user_id):
    """
    Deletes a user from the database by ID.

    Args:
        db: The database session object.
        user_id: The ID of the user to be deleted.

    Returns:
        A message confirming the deletion of the user.
    """
    try:
        # Fetch user from the database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        # Delete the user and commit the transaction
        db.delete(user)
        db.commit()
        
        logger.info(f"User {user.username} deleted successfully.")
        return {"message": f"User {user.username} deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

def create_admin(user: UserRegister, db: Session) -> User:
    """
    Creates a new admin user and stores it in the database.

    Args:
        user: A UserRegister object containing the username and password.
        db: The database session object.

    Returns:
        The created User object.
    """
    try:
        # Check if the user already exists
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
            
        # Hash the password and create the new admin user
        hashed_pw = hash_password(user.password)
        new_user = User(username=user.username, hashed_password=hashed_pw, is_admin=True)
        
        # Add the user and commit the transaction
        db.add(new_user)
        db.commit()
        
        logger.info(f"Admin user {new_user.username} created successfully.")
        return new_user
    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create admin user: {str(e)}"
        )

async def upload_files(files: List[UploadFile], tags: str, files_collection: AsyncIOMotorCollection, current_user: User, embed_data: EmbedData, vector_db: QdrantVDB):
    """
    Handles the file upload process, including checking for duplicates, extracting content, and embedding the data into a vector database.

    Args:
        files: A list of files to be uploaded.
        tags: Tags to associate with the uploaded files.
        files_collection: The MongoDB collection to store the file metadata.
        current_user: The current authenticated user uploading the files.
        embed_data: The object used to embed the extracted data.
        vector_db: The vector database for storing embedded data.

    Returns:
        A message indicating success or failure.
    """
    try:
        for file in files:
            try:
                file_bytes = await file.read() # Read the file bytes
                file_hash = get_file_hash(file_bytes) # Generate a hash for file uniqueness
                
                # Check if the file already exists in the database by hash
                existing_file = await files_collection.find_one({"file_hash": file_hash})
                if existing_file: 
                    logger.info(f"File {file.filename} already exists in the database, skipping upload.")
                    continue # Skip if file already exists
                
                # Generate a unique filename for the uploaded file
                unique_filename = get_unique_filename(file.filename)
                
                # Define file path for saving the uploaded file
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

                # Save the file to disk
                with open(file_path, "wb") as buffer:
                    buffer.write(file_bytes)
                
                # Extract data based on file type and embed it
                if await is_pdf(file_bytes):
                    extracted_data = extract_pdf_data(file_path=file_path, bot=bot)
                    if extracted_data:
                        texts, image_summaries, table_summaries = extracted_data
                        embed_data.embed(texts + image_summaries + table_summaries)
                    else:
                        logger.error("Failed to extract data from PDF.")
                        raise Exception("Failed to fetch extract data.")
                elif await is_txt(file_bytes):
                    extracted_data = extract_txt_data(file_path=file_path)
                    if extracted_data:
                        texts = extracted_data
                        embed_data.embed(texts)
                    else:
                        logger.error("Failed to extract data from TXT file.")
                        raise Exception("Failed to fetch extract data.")
                elif await is_image(file_bytes):
                    extracted_data = extract_image_data(file_path=file_path, bot=bot)
                    if extracted_data:
                        image_summaries = extracted_data
                        embed_data.embed(image_summaries)
                    else:
                        logger.error("Failed to extract data from image.")
                        raise Exception("Failed to fetch extract data.")
                
                # Prepare collection name and ingest data into vector DB
                collection_name = 'multimodal_rag_admin_collection'
                vector_db.create_or_set_collection(collection_name)
                vector_db.ingest_data(embed_data, source=file_path)
                
                # Metadata for storing in database
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
                
                # Insert file metadata into the database
                await files_collection.insert_one(metadata)
                logger.info(f"File {file.filename} uploaded and processed successfully.")
            except Exception as e:
                # Cleanup if any error occurs during processing
                if os.path.exists(file_path):
                    os.remove(file_path)
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                raise
        return {"message": f"Files uploaded successfully"}
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

async def list_all_files(files_collection: AsyncIOMotorCollection):
    """
    Lists all files uploaded by all users and admin.

    Args:
        files_collection: MongoDB collection containing file metadata.

    Returns:
        A list of dictionaries containing file metadata for files uploaded by all users and admin.
    """
    try:
        # Retrieve files from database and filter by all users and admin.
        files_list = await files_collection.find().to_list()
        return [{"id": str(file['_id']),
                "filename": file['filename'],
                "uploader": file['uploader'],
                "role": file['uploader_role'],
                "upload_time": file['upload_time'].strftime("%Y-%m-%d %H:%M:%S"),
                "collection_name": file['collection_name'],
                "tags": file['tags']} for file in files_list]
    except Exception as e:
        logger.error(f"Failed to fetch files meta data: {str(e)}")
        with open('error.txt', 'w') as f:
            f.write(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch files info : {str(e)}"
        )