import pytest, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session
from models.user import User
from config import Config
from auth.dependencies import verify_token, admin_only

@pytest.fixture
def mock_db_session():
    """Fixture to create a mocked SQLAlchemy session."""
    return MagicMock(spec=Session)

@pytest.fixture
def mock_user():
    """Fixture to create a mock user object."""
    user = MagicMock(spec=User)
    user.username = "testuser"
    user.is_admin = True
    return user

@patch("jose.jwt.decode")
def test_verify_token_valid(mock_jwt_decode, mock_db_session, mock_user, caplog):
    """Test verify_token with a valid token."""
    token_payload = {"sub": "testuser"}
    mock_jwt_decode.return_value = token_payload
    mock_db_session.query().filter().first.return_value = mock_user
    
    with caplog.at_level("INFO"):
        user = verify_token(token="valid_token", db=mock_db_session)
    
    assert user == mock_user
    mock_jwt_decode.assert_called_once_with("valid_token", Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
    mock_db_session.query.assert_called()
    assert "User 'testuser' successfully authenticated" in caplog.text

@patch("jose.jwt.decode")
@pytest.mark.parametrize("token_payload, expected_detail", [
    ({}, "Invalid token: Missing username"),
    ({"sub": "unknown_user"}, "Invalid token: User not found"),
])
def test_verify_token_invalid_token(mock_jwt_decode, mock_db_session, token_payload, expected_detail):
    """Test verify_token with an invalid payloads."""
    mock_jwt_decode.return_value = token_payload
    mock_db_session.query().filter().first.return_value = None if "unknown_user" in token_payload.values() else MagicMock()
    
    with pytest.raises(HTTPException) as exc:
        verify_token(token="invalid_token", db=mock_db_session)
    
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert expected_detail in exc.value.detail
    
@patch("jose.jwt.decode")
def test_verify_token_invalid_token(mock_jwt_decode, mock_db_session, caplog):
    """Test verify_token with an invalid token."""
    mock_jwt_decode.side_effect = JWTError("Invalid signature")
    
    with pytest.raises(HTTPException) as exc:
        verify_token(token="invalid_token", db=mock_db_session)
    
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid token" in exc.value.detail
    assert "Invalid token: Invalid signature" in caplog.text

@patch("jose.jwt.decode")
def test_verify_token_missing_username(mock_jwt_decode, mock_db_session):
    """Test verify_token with a token missing a username."""
    mock_jwt_decode.return_value = {}
    
    with pytest.raises(HTTPException) as exc:
        verify_token(token="no_username_token", db=mock_db_session)
    
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Missing username" in exc.value.detail

@patch("jose.jwt.decode")
def test_verify_token_user_not_found(mock_jwt_decode, mock_db_session):
    """Test verify_token when the user is not found in the database."""
    mock_jwt_decode.return_value = {"sub": "unknown_user"}
    mock_db_session.query().filter().first.return_value = None
    
    with pytest.raises(HTTPException) as exc:
        verify_token(token="valid_token", db=mock_db_session)
    
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "User not found" in exc.value.detail

# Tests for admin_only function
def test_admin_only_with_admin(mock_user, caplog):
    """Test admin_only function with an admin user."""
    with caplog.at_level("INFO"):
        assert admin_only(current_user=mock_user) == mock_user
        assert "Admin only verification success for user 'testuser'" in caplog.text

def test_admin_only_without_admin(mock_user, caplog):
    """Test admin_only function when user is not an admin."""
    mock_user.is_admin = False
    
    with pytest.raises(HTTPException) as exc:
        admin_only(current_user=mock_user)
    
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Admins only" in exc.value.detail
    assert "Access denied: User 'testuser' is not an admin" in caplog.text
