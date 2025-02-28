import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from unittest.mock import MagicMock
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.mongo_db import get_users_collection, get_files_collection

@pytest.fixture
def mock_mongo_db():
    """Fixture to create a mocked MongoDB database instance."""
    mock_db = MagicMock(spec=AsyncIOMotorDatabase)

    def get_mock_collection(name):
        collection_mock = MagicMock()
        collection_mock.name = name 
        return collection_mock

    mock_db.__getitem__.side_effect = get_mock_collection
    return mock_db

def test_get_users_collection(mock_mongo_db, mocker, caplog):
    """Test if get_users_collection fetches the 'users' collection."""
    mocker.patch("models.mongo_db.mongo_db_client", mock_mongo_db)
    with caplog.at_level("INFO"):
        users_collection = get_users_collection()
    
    assert users_collection.name == "users"    
    assert "Fetching 'users' collection from MongoDB." in caplog.text

def test_get_files_collection(mock_mongo_db, mocker, caplog):
    """Test if get_files_collection fetches the 'files' collection."""
    mocker.patch("models.mongo_db.mongo_db_client", mock_mongo_db)
    with caplog.at_level("INFO"):
        files_collection = get_files_collection()

    assert files_collection.name == "files"    
    assert "Fetching 'files' collection from MongoDB." in caplog.text
