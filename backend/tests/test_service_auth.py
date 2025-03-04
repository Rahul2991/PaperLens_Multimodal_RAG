import pytest, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.user import UserRegister, UserLogin
from auth.security import hash_password
from models.user import User
from services.auth import create_user, authenticate_user, create_access_token_for_user

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.username = "testuser"
    user.hashed_password = hash_password("password123")
    return user

@patch("auth.security.hash_password")
def test_create_user_success(mock_hash_password, mock_db_session, caplog):
    mock_hash_password.return_value = "hashed_password"
    mock_db_session.query().filter().first.return_value = None
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    
    user_data = UserRegister(username="newuser", password="securepassword")
    with caplog.at_level("INFO"):
        new_user = create_user(user_data, mock_db_session)
    
    assert new_user.username == "newuser"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    assert "User created successfully" in caplog.text

@patch("auth.security.hash_password")
def test_create_user_existing_username(mock_hash_password, mock_db_session, caplog):
    mock_hash_password.return_value = "hashed_password"
    mock_db_session.query().filter().first.return_value = MagicMock()
    
    user_data = UserRegister(username="existinguser", password="password")
    with pytest.raises(HTTPException) as exc:
        create_user(user_data, mock_db_session)
    
    assert exc.value.status_code == 400
    assert "Username already exists" in exc.value.detail
    assert "Username already exists: " in caplog.text
    
@patch("auth.security.hash_password")
def test_create_user_error(mock_hash_password, mock_db_session, caplog):
    mock_hash_password.return_value = "hashed_password"
    mock_db_session.query().filter().first.return_value = None
    mock_db_session.commit = Exception()
    
    user_data = UserRegister(username="existinguser", password="password")
    with pytest.raises(HTTPException) as exc:
        create_user(user_data, mock_db_session)
    
    assert exc.value.status_code == 500
    assert "Failed to create user" in exc.value.detail
    assert "Error creating user: " in caplog.text

@patch("auth.security.verify_password")
def test_authenticate_user_success(mock_verify_password, mock_db_session, mock_user, caplog):
    mock_verify_password.return_value = True
    mock_db_session.query().filter().first.return_value = mock_user
    user_data = UserLogin(username="testuser", password="password123")
    
    with caplog.at_level("INFO"):
        user = authenticate_user(user_data, mock_db_session)
        
    assert user == mock_user
    assert "User 'testuser' successfully authenticated." in caplog.text

@patch("auth.security.verify_password")
def test_authenticate_user_invalid_credentials(mock_verify_password, mock_db_session, caplog):
    mock_verify_password.return_value = False
    mock_db_session.query().filter().first.return_value = None
    user_data = UserLogin(username="invaliduser", password="wrongpass")
    
    with pytest.raises(HTTPException) as exc:
        authenticate_user(user_data, mock_db_session)
    
    assert exc.value.status_code == 401
    assert "Invalid username or password" in exc.value.detail
    assert "Authentication failed for user: invaliduser" in caplog.text

@patch("auth.security.jwt.encode")
def test_create_access_token_for_user(mock_jwt_encode, caplog):
    mock_jwt_encode.return_value = "mocked_token"
    user_data = UserLogin(username="testuser", password="password123")
    
    with caplog.at_level("INFO"):
        token = create_access_token_for_user(user_data, is_admin=True)
    
    mock_jwt_encode.assert_called_once()
    assert token == "mocked_token"
    assert "Access token generated for user: testuser" in caplog.text
