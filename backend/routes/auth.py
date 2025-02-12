from fastapi import APIRouter, Depends
from models.sql_db import get_db
from sqlalchemy.orm import Session
from schemas.user import UserRegister, UserLogin, LoginResponse, RegisterResponse
from services.auth import create_user, authenticate_user, create_access_token_for_user

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    new_user = create_user(user, db)
    return {"message": "User registered successfully", "username": new_user.username}

@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(user, db)
    access_token = create_access_token_for_user(user, db_user.is_admin)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login successful",
        "username": user.username,
        "is_admin": db_user.is_admin,
    }