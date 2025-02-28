import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from unittest.mock import patch
from services.rag_service import get_vector_db, get_embed_data_obj

@pytest.fixture
def mock_qdrant_vdb():
    """Fixture to patch QdrantVDB where it's used."""
    with patch("services.rag_service.QdrantVDB") as MockQdrantVDB:
        yield MockQdrantVDB.return_value  # Returns the mock instance

@pytest.fixture
def mock_embed_data():
    """Fixture to patch EmbedData where it's used."""
    with patch("services.rag_service.EmbedData") as MockEmbedData:
        yield MockEmbedData.return_value

@pytest.fixture
def mock_conversational_bot():
    """Fixture to patch Conversational_Bot where it's used."""
    with patch("services.rag_service.Conversational_Bot") as MockConversationalBot:
        yield MockConversationalBot.return_value

def test_get_vector_db(mock_qdrant_vdb):
    result = get_vector_db()
    assert result is mock_qdrant_vdb  # Ensures mock is returned

def test_get_embed_data_obj(mock_embed_data):
    result = get_embed_data_obj()
    assert result is mock_embed_data  # Ensures mock is returned

def test_conversational_bot_initialization(mock_conversational_bot):
    from services.rag_service import Conversational_Bot  # Import after patching

    bot_instance = Conversational_Bot()  # Should use the patched version
    assert bot_instance is mock_conversational_bot