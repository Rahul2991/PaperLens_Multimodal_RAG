import pytest, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock, patch
from rag_modules.conversational_bot import Conversational_Bot
from rag_modules.document_extract import (
    extract_pdf_data, extract_txt_data, extract_image_data
)
import unstructured.documents.elements as elements

@pytest.fixture
def mock_bot():
    bot = Conversational_Bot()
    bot.summarize_image = MagicMock(return_value="Mocked image summary")
    bot.summarize_table = MagicMock(return_value="Mocked table summary")
    return bot

@pytest.fixture
def mock_pdf_data():
    return [
        elements.Table(text="Sample table", detection_origin="test"),
        elements.CompositeElement(text="Sample text", metadata=elements.ElementMetadata(orig_elements=[elements.Image(text="Sample image", detection_origin="test")])),
        ]

@pytest.fixture
def mock_text_data():
    return [elements.CompositeElement(text="Sample text document")]
@patch("os.path.exists")
@patch("rag_modules.document_extract.partition_pdf")
def test_extract_pdf_data(mock_partition_pdf, mock_path_exist, mock_pdf_data, mock_bot):
    mock_partition_pdf.return_value = mock_pdf_data
    mock_path_exist.return_value = True
    texts, image_summaries, table_summaries = extract_pdf_data(file_path="dummy.pdf", bot=mock_bot)
    assert len(texts) == 1
    assert len(image_summaries) == 1
    assert len(table_summaries) == 1
    mock_bot.summarize_image.assert_called()
    mock_bot.summarize_table.assert_called()
    
@patch("os.path.exists")
@patch("rag_modules.document_extract.partition_text")
def test_extract_txt_data(mock_partition_text, mock_path_exist, mock_text_data):
    mock_partition_text.return_value = mock_text_data
    mock_path_exist.return_value = True
    texts = extract_txt_data(file_path="dummy.txt")
    
    assert len(texts) == 1
    assert "Sample text document" in texts

@patch("os.path.exists", return_value=True)
def test_extract_image_data(mock_path_exist, mock_bot):
    mock_path_exist.return_value = True
    image_summary = extract_image_data(file_path="dummy.jpg", bot=mock_bot)
    
    assert image_summary == "Mocked image summary"
    mock_bot.summarize_image.assert_called()