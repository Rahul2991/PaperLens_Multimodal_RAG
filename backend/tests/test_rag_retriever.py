import pytest, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock
from rag_modules.vector_db import QdrantVDB
from rag_modules.embed_data import EmbedData
from rag_modules.rag_retriever import Retriever

@pytest.fixture
def mock_vector_db():
    """Fixture to create a mocked QdrantVDB instance."""
    mock_db = MagicMock(spec=QdrantVDB)
    mock_db.collection_name = "test_collection"
    mock_db.client = MagicMock()
    mock_db.client.query_points.return_value = [{"context": "sample result", "source": "test_source"}]
    return mock_db

@pytest.fixture
def mock_embed_data():
    """Fixture to create a mocked EmbedData instance."""
    mock_embed = MagicMock(spec=EmbedData)
    mock_embed.embed_model = MagicMock()
    mock_embed.embed_model.get_query_embedding.return_value = [0.1, 0.2, 0.3]  # Mocked embedding output
    return mock_embed

def test_retriever_initialization(mock_vector_db, mock_embed_data):
    """Test if Retriever initializes correctly."""
    retriever = Retriever(vector_db=mock_vector_db, embeddata=mock_embed_data)
    
    assert retriever.vector_db == mock_vector_db
    assert retriever.embeddata == mock_embed_data

def test_search(mock_vector_db, mock_embed_data):
    """Test if search correctly retrieves results from Qdrant."""
    retriever = Retriever(vector_db=mock_vector_db, embeddata=mock_embed_data)
    
    query = "Test query"
    results = retriever.search(query, top_k=5)

    assert results is not None
    assert isinstance(results, list)
    assert "context" in results[0]
    assert "source" in results[0]
    
    mock_embed_data.embed_model.get_query_embedding.assert_called_once_with(query)
    mock_vector_db.client.query_points.assert_called_once()

def test_search_handles_exceptions(mock_vector_db, mock_embed_data, caplog):
    """Test if search handles exceptions gracefully."""
    mock_vector_db.client.query_points.side_effect = Exception("Mocked search error")
    retriever = Retriever(vector_db=mock_vector_db, embeddata=mock_embed_data)

    results = retriever.search("Test query", top_k=5)

    assert results is None
    assert "Error occurred during search: Mocked search error" in caplog.text