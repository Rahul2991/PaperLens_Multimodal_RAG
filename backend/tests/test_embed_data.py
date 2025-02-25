import pytest, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock, patch
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from rag_modules.embed_data import EmbedData

@pytest.fixture
def mock_embed_model():
    """Fixture to create a mocked embedding model."""
    mock_model = MagicMock(spec=HuggingFaceEmbedding)
    mock_model.get_text_embedding_batch.return_value = [[0.1, 0.2, 0.3]]  # Mocked embedding output
    return mock_model

@patch("rag_modules.embed_data.HuggingFaceEmbedding")
def test_embed_model_initialization(mock_huggingface_embedding):
    """Test if the embedding model initializes correctly."""
    mock_huggingface_embedding.return_value = MagicMock()

    embedder = EmbedData()
    assert embedder.embed_model is not None
    mock_huggingface_embedding.assert_called_once_with(model_name="nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
    
@patch("rag_modules.embed_data.HuggingFaceEmbedding")
def test_load_embed_model_exception(mock_huggingface_embedding, caplog):
    """Test if _load_embed_model() correctly handles an exception when model loading fails."""
    
    # Make the mocked HuggingFaceEmbedding raise an exception
    mock_huggingface_embedding.side_effect = RuntimeError("Mocked model load error")

    with pytest.raises(RuntimeError, match="Mocked model load error"):
        embedder = EmbedData()  # This will trigger exception for _load_embed_model()

    # Check if the error was logged
    assert "Error loading embedding model: Mocked model load error" in caplog.text

def test_generate_embedding(mock_embed_model):
    """Test if generate_embedding correctly calls the model."""
    embedder = EmbedData()
    embedder.embed_model = mock_embed_model

    text_input = ["Hello world!"]
    embeddings = embedder.generate_embedding(text_input)

    assert len(embeddings) == 1
    assert isinstance(embeddings[0], list)  # Check if output is a list
    mock_embed_model.get_text_embedding_batch.assert_called_once_with(text_input)

def test_batch_iterate():
    """Test if batch_iterate correctly divides data into batches."""
    embedder = EmbedData(batch_size=2)
    sample_data = ["text1", "text2", "text3", "text4", "text5"]

    batches = list(embedder.batch_iterate(sample_data, batch_size=2))

    assert len(batches) == 3  # 2 + 2 + 1
    assert batches[0] == ["text1", "text2"]
    assert batches[1] == ["text3", "text4"]
    assert batches[2] == ["text5"]
    
def test_embed(mock_embed_model):
    """Test if embedding are generated for provided list of texts."""
    embedder = EmbedData()
    embedder.embed_model = mock_embed_model
    sample_texts = ["Hello world!"]
    embedder.embed(sample_texts)

    assert len(embedder.embeddings) == 1
    assert isinstance(embedder.embeddings[0], list)
    
def test_embed_exception(mock_embed_model, caplog):
    """Test if embed() correctly raises an exception when an error occurs."""
    embedder = EmbedData()
    embedder.embed_model = mock_embed_model  # Inject the mocked model
    
    # Mock generate_embedding to raise an exception
    embedder.generate_embedding = MagicMock(side_effect=RuntimeError("Mocked error"))

    sample_texts = ["Hello world!", "This is a test."]

    with pytest.raises(RuntimeError, match="Mocked error"):
        embedder.embed(sample_texts)
        
    # Check if the error was logged
    assert "Error during embedding: Mocked error" in caplog.text