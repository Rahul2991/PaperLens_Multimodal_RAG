import pytest, sys, os, io
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import AsyncMock, MagicMock, patch
from rag_modules.rag import RAG
from fastapi import UploadFile
from models.user import User
from cache import user_sessions_cache
from services.chat_service import get_user_sessions, delete_session_data, chat_bot

@pytest.fixture
def mock_user():
    """Fixture for a mock authenticated user"""
    return User(username="test_user")

@pytest.fixture
def mock_user_session(mock_user):
    """Fixture for a mock user session"""
    return {
        "_id": "1",
        "username": mock_user.username,
        "chat_sessions": [{"session_id": "abc123", "messages": [], "bot_chat_history": ['System Instructions']},
                        {"session_id": "xyz456", "messages": [], "bot_chat_history": ['System Instructions']}]
    }

@pytest.fixture
def mock_users_collection(mock_user):
    """Fixture for a mock MongoDB collection"""
    mock_collection = AsyncMock()
    mock_collection.find_one = AsyncMock(return_value=None)  # Simulating user not found
    mock_collection.insert_one = AsyncMock(return_value=AsyncMock(inserted_id="mock_id"))
    return mock_collection

@pytest.fixture
def clear_cache():
    """Fixture to clear the user session cache before each test"""
    user_sessions_cache.clear()

@pytest.mark.asyncio
async def test_get_user_sessions_new_user(mock_user, mock_users_collection, clear_cache):
    """Test case where the user does not exist in the database, and a new entry is created."""
    print(mock_user)
    print(mock_users_collection)
    user_session = await get_user_sessions(
        current_user=mock_user, users_collection=mock_users_collection
    )

    assert user_session["username"] == mock_user.username
    assert user_session["chat_sessions"] == []
    mock_users_collection.find_one.assert_called_once_with({"username": "test_user"})
    mock_users_collection.insert_one.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_user_sessions_existing_user(mock_user, mock_users_collection, clear_cache):
    """Test case where the user already exists in the cache, so database query is skipped."""
    # Simulate existing session in cache
    user_sessions_cache[mock_user.username] = {"username": mock_user.username, "chat_sessions": ["session1"]}

    user_session = await get_user_sessions(
        current_user=mock_user, users_collection=mock_users_collection
    )
    
    assert user_session["username"] == mock_user.username
    assert user_session["chat_sessions"] == ["session1"]
    mock_users_collection.find_one.assert_not_called() 

@pytest.mark.asyncio
async def test_get_user_sessions_existing_user_in_db(mock_user, mock_users_collection, clear_cache):
    """Test case where the user exists in the database but not in the cache."""
    mock_users_collection.find_one.return_value = {"username": mock_user.username, "chat_sessions": ["session2"]}

    user_session = await get_user_sessions(
        current_user=mock_user, users_collection=mock_users_collection
    )

    assert user_session["username"] == mock_user.username
    assert user_session["chat_sessions"] == ["session2"]
    mock_users_collection.find_one.assert_called_once_with({"username": "test_user"})

@pytest.mark.asyncio
async def test_get_user_sessions_cache_corrupted(mock_user, mock_users_collection, clear_cache):
    """Test case when cache contains invalid data, forcing a database fetch."""
    user_sessions_cache[mock_user.username] = "corrupted_data"  # Simulating corruption

    user_session = await get_user_sessions(current_user=mock_user, users_collection=mock_users_collection)

    assert isinstance(user_session, dict)
    mock_users_collection.find_one.assert_called_once()
    
@pytest.mark.asyncio
async def test_get_user_sessions_mongo_insert_failure(mock_user, mock_users_collection, clear_cache):
    """Test case when MongoDB fails to insert a new user."""
    mock_users_collection.insert_one.side_effect = Exception("MongoDB Insert Error")

    with pytest.raises(Exception, match="MongoDB Insert Error"):
        await get_user_sessions(current_user=mock_user, users_collection=mock_users_collection)
        
@pytest.mark.asyncio
async def test_delete_session(mock_user, mock_user_session, mock_users_collection, clear_cache):
    """Test case for successfully deleting a session."""
    user_sessions_cache[mock_user.username] = mock_user_session

    await delete_session_data(session_id="abc123", user=mock_user_session, users_collection=mock_users_collection)

    updated_sessions = user_sessions_cache[mock_user.username]["chat_sessions"]
    assert len(updated_sessions) == 1
    assert updated_sessions[0]["session_id"] == "xyz456"
    mock_users_collection.update_one.assert_awaited_once()
    
@patch('ollama.chat')
@pytest.mark.asyncio
async def test_chat_bot_no_rag(mock_bot, mock_user, mock_user_session, mock_users_collection, clear_cache):
    """Test case for chatbot response in 'no-rag' mode."""
    mock_bot.return_value = MagicMock(message=MagicMock(content="Test AI response"))
    
    user_sessions_cache[mock_user.username] = mock_user_session

    response, session = await chat_bot(
        session_id="abc123", 
        message="Hello, AI!", 
        rag_mode="no-rag", 
        user=mock_user_session, 
        users_collection=mock_users_collection, 
        current_user=mock_user, 
        embed_data=MagicMock(), 
        vector_db=MagicMock()
    )

    assert response.message.content == "Test AI response"
    assert session["messages"][-1]["role"] == "bot"
    assert session["messages"][-1]["text"] == "Test AI response"
    
@patch('ollama.chat')
@pytest.mark.asyncio
async def test_chat_bot_with_image(mock_bot, mock_user, mock_user_session, mock_users_collection, clear_cache):
    """Test case for chatbot response when an image is uploaded."""
    mock_bot.return_value = MagicMock(message=MagicMock(content="Image processed."))
    
    user_sessions_cache[mock_user.username] = mock_user_session

    image_mock = UploadFile(filename="test.jpg", file=io.BytesIO(b"fake_image_data"))

    response, session = await chat_bot(
        session_id="abc123",
        message="Analyze this image",
        image=image_mock,
        rag_mode="no-rag",
        user=mock_user_session,
        users_collection=mock_users_collection,
        current_user=mock_user,
        embed_data=MagicMock(),
        vector_db=MagicMock()
    )

    assert response.message.content == "Image processed."
    assert session["messages"][-1]["role"] == "bot"
    assert session["messages"][-1]["text"] == "Image processed."

@pytest.mark.asyncio
async def test_chat_bot_rag_mode_all(mock_user, mock_user_session, mock_users_collection, clear_cache):
    """Test case for chatbot response in 'all' RAG mode."""
    mock_rag_output = MagicMock()
    mock_rag_output.message.content = "RAG response"
    
    user_sessions_cache[mock_user.username] = mock_user_session
    
    with patch.object(RAG, 'query', return_value=mock_rag_output) as mock_rag:
        response, session = await chat_bot(
            session_id="abc123",
            message="Retrieve relevant data",
            rag_mode="all",
            user=mock_user_session,
            users_collection=mock_users_collection,
            current_user=mock_user,
            embed_data=MagicMock(),
            vector_db=MagicMock(),
        )

    assert response.message.content == "RAG response"
    assert session["messages"][-1]["role"] == "bot"
    assert session["messages"][-1]["text"] == "RAG response"
    
@pytest.mark.asyncio
async def test_chat_bot_rag_mode_user(mock_user, mock_user_session, mock_users_collection, clear_cache):
    """Test case for chatbot response in 'user' RAG mode."""
    mock_rag_output = MagicMock()
    mock_rag_output.message.content = "User RAG response"
    
    user_sessions_cache[mock_user.username] = mock_user_session
    
    with patch.object(RAG, 'query', return_value=mock_rag_output) as mock_rag:
        response, session = await chat_bot(
            session_id="abc123",
            message="Retrieve relevant data",
            rag_mode="all",
            user=mock_user_session,
            users_collection=mock_users_collection,
            current_user=mock_user,
            embed_data=MagicMock(),
            vector_db=MagicMock(),
        )

    assert response.message.content == "User RAG response"
    assert session["messages"][-1]["role"] == "bot"
    assert session["messages"][-1]["text"] == "User RAG response"