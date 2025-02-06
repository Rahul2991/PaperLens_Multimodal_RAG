from fastapi import APIRouter, Depends, File, UploadFile
from auth.dependencies import verify_token
from models.mongo_db import get_files_collection
from models.user import User
from services.rag_service import get_embed_data_obj, get_vector_db
from models.sql_db import get_db
from sqlalchemy.orm import Session
from schemas.user import UserRegister, UserLogin, LoginResponse, RegisterResponse
from services.user import create_user, authenticate_user, create_access_token_for_user

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    new_user = create_user(user, db)
    return {"message": "User registered successfully", "username": new_user.username}

@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(user, db)
    access_token = create_access_token_for_user(user)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login successful",
        "username": user.username,
        "is_admin": db_user.is_admin,
    }
    
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    current_user: User = Depends(verify_token), 
    files_collection = Depends(get_files_collection),
    embed_data = Depends(get_embed_data_obj),
    vector_db = Depends(get_vector_db)
    ):
    await upload_file(file, files_collection, current_user, embed_data, vector_db)

    return {"message": f"File uploaded: '{file.filename}'"}