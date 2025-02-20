from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.sql_db import get_db
from jose import JWTError, jwt
from models.user import User
from config import Config
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

# OAuth2 Password Bearer token scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Verifies and decodes a JWT token, then fetches the corresponding user from the database.

    Args:
        token (str): The JWT token obtained from the authorization header.
        db (Session): Database session dependency.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If the token is invalid, missing username, or the user is not found.
    """
    try:
        # Decode the JWT token using the secret key and algorithm
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        username: str = payload.get("sub") # Extract username (subject) from token
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: Missing username",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Query the database for the user
        user = db.query(User).filter(User.username == username).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"User '{username}' successfully authenticated")
        return user
    except JWTError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
def admin_only(current_user: User = Depends(verify_token)):
    """
    Ensures that only users with admin privileges can access certain endpoints.

    Args:
        current_user (User): The authenticated user.

    Returns:
        User: The authenticated admin user.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if not current_user.is_admin:
        logger.warning(f"Access denied: User '{current_user.username}' is not an admin")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admins only",
        )
    logger.info(f"Admin only verification success for user '{current_user.username}'")
    return current_user