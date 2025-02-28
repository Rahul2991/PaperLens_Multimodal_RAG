import pytest, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock
from rag_modules.rag import RAG
from rag_modules.rag_retriever import Retriever
from rag_modules.conversational_bot import Conversational_Bot

@pytest.fixture
def mock_retriever():
    """Fixture to create a mocked Retriever instance."""
    retriever = MagicMock(spec=Retriever)
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "points": [
            {"payload": {"context": "Document 1 content"}},
            {"payload": {"context": "Document 2 content"}}
        ]
    }
    retriever.search.return_value = mock_response
    return retriever

@pytest.fixture
def mock_bot():
    """Fixture to create a mocked Conversational_Bot instance."""
    bot = MagicMock(spec=Conversational_Bot)
    bot.generate.return_value = "This is a generated response."
    return bot

@pytest.fixture
def rag(mock_retriever, mock_bot):
    """Fixture to create a mocked RAG instance."""
    return RAG(retriever=mock_retriever, bot=mock_bot)

def test_rerank(rag):
    """Test if rerank function correctly filter retrieved results."""
    retrieved_docs = [
        {"payload": {"context": "Relevant document"}, "score": 0.8},
        {"payload": {"context": "Irrelevant document"}, "score": 0.5}
    ]
    rag.reranker_model = MagicMock()
    rag.tokenizer = MagicMock()
    mock_rerank_output = MagicMock()
    mock_rerank_output.logits.squeeze.return_value.tolist.return_value = [0.8, 0.5]
    rag.reranker_model.return_value = mock_rerank_output
    
    reranked_docs = rag.rerank("test query", retrieved_docs)
    
    assert len(reranked_docs) == 1
    assert reranked_docs[0]["payload"]["context"] == "Relevant document"

def test_generate_context(rag):
    """Test if generate_context function correctly generates relevant context."""
    rag.reranker_model = MagicMock()
    rag.tokenizer = MagicMock()
    mock_rerank_output = MagicMock()
    mock_rerank_output.logits.squeeze.return_value.tolist.return_value = [1.0, 0.8]
    rag.reranker_model.return_value = mock_rerank_output
    context = rag.generate_context("test query")
    assert isinstance(context, str)
    assert "Document 1 content" in context
    assert "Document 2 content" in context
    assert "Document 1 content" in context.split("\n")  # Ensure correct formatting

def test_query(rag):
    """Test if query function correctly generates response."""
    response = rag.query("test query")
    assert response == "This is a generated response."