import pytest, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datetime import timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from unittest.mock import patch
from config import Config
from auth.security import create_access_token, hash_password, verify_password

SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test create_access_token
def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    
    # Decode and validate the token
    decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_data["sub"] == "testuser"
    assert "exp" in decoded_data

def test_create_access_token_with_custom_expiry():
    data = {"sub": "testuser"}
    expiry = timedelta(minutes=5)
    token = create_access_token(data, expires_delta=expiry)
    
    decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_data["sub"] == "testuser"

def test_create_access_token_invalid():
    with patch("auth.security.jwt.encode", side_effect=JWTError):
        with pytest.raises(JWTError):
            create_access_token({"sub": "testuser"})

# Test password hashing and verification
def test_hash_password():
    password = "securepassword"
    hashed_pw1 = hash_password(password)
    hashed_pw2 = hash_password(password)
    
    assert isinstance(hashed_pw1, str)
    assert hashed_pw1 != password  # Ensure it's hashed
    assert hashed_pw1 != hashed_pw2

def test_verify_password():
    password = "securepassword"
    hashed_pw = hash_password(password)
    
    assert verify_password(password, hashed_pw) == True
    assert verify_password("wrongpassword", hashed_pw) == False
