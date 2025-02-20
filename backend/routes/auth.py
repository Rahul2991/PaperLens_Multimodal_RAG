from fastapi import APIRouter, Depends
from models.sql_db import get_db
from sqlalchemy.orm import Session
from schemas.user import UserRegister, UserLogin, LoginResponse, RegisterResponse
from services.auth import create_user, authenticate_user, create_access_token_for_user
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

# Create a FastAPI router for authentication-related endpoints
router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """
    Registers a new user.
    
    Args:
        user (UserRegister): The user registration data.
        db (Session): Database session dependency.

    Returns:
        dict: A success message along with the registered username.
    """
    logger.info(f"Registering new user: {user.username}")
    
    # Create a new user in the database
    new_user = create_user(user, db)
    
    logger.info(f"User {new_user.username} registered successfully.")
    
    return {"message": "User registered successfully", "username": new_user.username}

@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns an access token.
    
    Args:
        user (UserLogin): The user login data.
        db (Session): Database session dependency.

    Returns:
        dict: Access token, token type, success message, username, and admin status.
    """
    logger.info(f"User {user.username} attempting to log in.")
    
    # Authenticate user credentials
    db_user = authenticate_user(user, db)
    
    # Generate access token for the authenticated user
    access_token = create_access_token_for_user(user, db_user.is_admin)
    
    logger.info(f"User {user.username} logged in successfully. Admin: {db_user.is_admin}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login successful",
        "username": user.username,
        "is_admin": db_user.is_admin,
    }