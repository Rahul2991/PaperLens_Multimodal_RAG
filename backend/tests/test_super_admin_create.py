import pytest, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sqlalchemy import create_engine
from unittest.mock import MagicMock
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models.user import User, Base
from models.super_admin_create import create_super_admin

# Setup an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def setup_db():
    """Fixture to set up the database schema before running tests."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(setup_db):
    """Fixture to provide a clean database session for each test."""
    session = TestingSessionLocal()
    yield session
    session.close()

def test_create_super_admin_success(db_session, caplog):
    """Test if a super admin is created successfully."""
    with caplog.at_level("INFO"):
        create_super_admin("admin_user", "secure_password", db_session)
    
    # Check if the user is stored in the database
    user = db_session.query(User).filter_by(username="admin_user").first()
    assert user is not None
    assert user.username == "admin_user"
    assert user.is_admin == 1
    assert user.hashed_password != "secure_password"  # Ensure password is hashed

    # Check if logging was called correctly
    assert "Creating super admin with username: admin_user" in caplog.text
    assert "Super admin created successfully" in caplog.text
    assert "Database session closed" in caplog.text

def test_create_super_admin_duplicate(db_session, caplog):
    """Test if the function handles duplicate usernames correctly."""
    
    with caplog.at_level("INFO"):
        create_super_admin("duplicate_user", "password123", db_session)
        
        # Attempt to create the same admin again
        create_super_admin("duplicate_user", "newpassword", db_session)
    
    # There should still be only one user with this username
    users = db_session.query(User).filter_by(username="duplicate_user").all()
    assert len(users) == 1  # Only one instance should exist

    # Verify logging for the error
    assert "Duplicate user error creating super admin: duplicate_user" in caplog.text
    assert "Database session closed" in caplog.text

def test_create_super_admin_failure(db_session, caplog):
    """Test if the function handles unexpected database failures."""
    db_session.commit = MagicMock(side_effect=SQLAlchemyError("Simulated DB failure"))
    db_session.close()  # Simulate a closed session error
    
    with caplog.at_level("INFO"):
        create_super_admin("fail_user", "fail_password", db_session)
    
    print(caplog.text)
    # Verify that an error log was triggered
    assert "Error creating super admin: Simulated DB failure" in caplog.text
    assert "Database session closed" in caplog.text
