import pytest, sys, os, grpc
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock, patch
from qdrant_client import QdrantClient
from rag_modules.vector_db import QdrantVDB

@pytest.fixture
def mock_qdrant_client():
    """Fixture to create a mocked QdrantClient instance."""
    mock_client = MagicMock(spec=QdrantClient)
    mock_client.collection_exists.return_value = False  # Simulate new collection scenario
    return mock_client

@pytest.fixture
def qdrant_vdb(mock_qdrant_client):
    """Fixture to initialize QdrantVDB with mocked client."""
    with patch("rag_modules.vector_db.QdrantClient", return_value=mock_qdrant_client):
        return QdrantVDB(vector_dim=768, batch_size=512, url="http://test-qdrant:6333")

def test_qdrant_vdb_initialization(qdrant_vdb):
    """Test if QdrantVDB initializes correctly."""
    assert qdrant_vdb.vector_dim == 768
    assert qdrant_vdb.batch_size == 512
    assert isinstance(qdrant_vdb.client, QdrantClient)

def test_create_or_set_collection(qdrant_vdb, mock_qdrant_client):
    """Test collection creation and existing collection handling."""
    qdrant_vdb.create_or_set_collection("test_collection")

    mock_qdrant_client.collection_exists.assert_called_once_with(collection_name="test_collection")
    mock_qdrant_client.create_collection.assert_called_once()

def test_create_or_set_collection_existing(qdrant_vdb, mock_qdrant_client):
    """Test when the collection already exists."""
    mock_qdrant_client.collection_exists.return_value = True
    qdrant_vdb.create_or_set_collection("existing_collection")

    mock_qdrant_client.collection_exists.assert_called_once_with(collection_name="existing_collection")
    mock_qdrant_client.create_collection.assert_not_called()
    
def test_qdrant_vdb_random_string_url(caplog):
    """Test QdrantVDB initialization with a random non-URL string."""
    with pytest.raises(Exception) as exc_info:
        QdrantVDB(vector_dim=768, batch_size=512, url="random_string")

    assert "Invalid URL" in caplog.text
    assert isinstance(exc_info.value, Exception)
    
def test_qdrant_vdb_unreachable_server(qdrant_vdb, mock_qdrant_client, caplog):
    """Test QdrantVDB when API call with to an unreachable server."""
    
    # Make the client collection_exists raise the grpc error
    mock_qdrant_client.collection_exists.side_effect = grpc.RpcError("Failed to connect to Qdrant server")

    with pytest.raises(grpc.RpcError):
        qdrant_vdb.create_or_set_collection("test_collection")

    # Check if the error message is properly logged
    assert "Failed to connect to Qdrant server" in caplog.text

def test_batch_iterate(qdrant_vdb):
    """Test batch iteration generator."""
    sample_data = list(range(10))
    batches = list(qdrant_vdb.batch_iterate(sample_data, batch_size=4))

    assert len(batches) == 3  # [0-3], [4-7], [8-9]
    assert batches[0] == [0, 1, 2, 3]
    assert batches[-1] == [8, 9]

def test_ingest_data(qdrant_vdb, mock_qdrant_client):
    """Test data ingestion with batched processing."""
    mock_embeddata = MagicMock()
    mock_embeddata.contexts = ["Context A", "Context B", "Context C", "Context D"]
    mock_embeddata.embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6], [0.7, 0.8]]

    qdrant_vdb.collection_name = "test_collection"
    qdrant_vdb.ingest_data(mock_embeddata, source="test_source")

    assert mock_qdrant_client.upload_collection.called
    assert mock_qdrant_client.update_collection.called

def test_ingest_data_handles_exceptions(qdrant_vdb, mock_qdrant_client, caplog):
    """Test exception handling during ingestion."""
    mock_embeddata = MagicMock()
    mock_embeddata.contexts = ["Context A", "Context B"]
    mock_embeddata.embeddings = [[0.1, 0.2], [0.3, 0.4]]

    # Mock upload_collection to raise an exception
    mock_qdrant_client.upload_collection.side_effect = Exception("Mocked upload error")

    qdrant_vdb.collection_name = "test_collection"

    with pytest.raises(Exception, match="Mocked upload error"):
        qdrant_vdb.ingest_data(mock_embeddata, source="test_source")

    # Check if the error was logged
    assert "Error during data ingestion: Mocked upload error" in caplog.text