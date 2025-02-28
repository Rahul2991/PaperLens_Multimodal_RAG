import pytest, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import patch, MagicMock
from rag_modules.conversational_bot import Conversational_Bot

@pytest.fixture
def bot():
    return Conversational_Bot(system="Test system instruction")

@patch("rag_modules.conversational_bot.ollama.chat")
def test_generate_text(mock_chat, bot):
    # Mocking ollama.chat response
    mock_response = MagicMock()
    mock_response.message.content = "Mocked response."
    mock_chat.return_value = mock_response
    
    user_input = "Hello, how are you?"
    response = bot.generate(user_input)
    
    # Assertions
    mock_chat.assert_called_once()
    assert response.message.content == "Mocked response."
    assert bot.messages[-1]["content"] == "Mocked response."
    assert bot.messages[-2]["content"] == user_input

@patch("rag_modules.conversational_bot.ollama.chat")
def test_generate_with_image(mock_chat, bot):
    # Mocking ollama.chat response
    mock_response = MagicMock()
    mock_response.message.content = "Mocked response with image."
    mock_chat.return_value = mock_response
    
    user_input = "Describe this image."
    image_path = "path/to/image.jpg"
    response = bot.generate(user_input, image=image_path)
    
    # Assertions
    mock_chat.assert_called_once()
    assert response.message.content == "Mocked response with image."
    assert bot.messages[-1]["content"] == "Mocked response with image."
    assert bot.messages[-2]["content"] == user_input
    assert bot.messages[-2]["images"] == [image_path]
