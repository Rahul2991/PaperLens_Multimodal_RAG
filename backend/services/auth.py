from sqlalchemy.orm import Session
from schemas.user import UserRegister, UserLogin
from auth.security import hash_password, verify_password, create_access_token
from datetime import timedelta
from models.user import User
from fastapi import HTTPException, status
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

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
    """
    Authenticates a user by verifying their credentials.

    Args:
        user (UserLogin): The login data containing username and password.
        db (Session): The database session.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If the username does not exist or the password is incorrect.
    """
    logger.info(f"Authenticating user: {user.username}")
    
    # Fetch user from the database
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        logger.warning(f"Authentication failed for user: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    logger.info(f"User '{user.username}' successfully authenticated.")
    return db_user

def create_access_token_for_user(user: UserLogin, is_admin: bool) -> str:
    """
    Generates an access token for the authenticated user.

    Args:
        user (UserLogin): The authenticated user object.
        is_admin (bool): Boolean flag indicating if the user is an admin.

    Returns:
        str: The generated JWT access token.
    """
    expiration = timedelta(minutes=60) if is_admin else None
    logger.info(f"Creating access token for user: {user.username} (Admin: {is_admin})")

    access_token = create_access_token(data={"sub": user.username}, expires_delta=expiration)
    
    logger.info(f"Access token generated for user: {user.username}")
    return access_token