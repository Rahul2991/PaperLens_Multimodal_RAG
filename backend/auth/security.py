from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
from config import Config
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

# Load security configurations from the Config module
SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Generates a JSON Web Token (JWT) for authentication.

    Args:
        data (dict): The data to be encoded in the token.
        expires_delta (timedelta, optional): Custom expiration duration for the token. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    
    # Set the token expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Encode the token with the secret key and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    logger.info(f"Access token created for user: {data.get('sub', 'unknown')} with expiration: {expire}")
    return encoded_jwt

def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    hashed_pw = pwd_context.hash(password)
    logger.info("Password successfully hashed.")
    return hashed_pw

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password against its hashed version.

    Args:
        plain_password (str): The plain text password entered by the user.
        hashed_password (str): The stored hashed password.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    is_valid = pwd_context.verify(plain_password, hashed_password)
    if is_valid:
        logger.info("Password verification successful.")
    else:
        logger.warning("Password verification failed.")
    return is_valid