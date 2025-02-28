from unstructured.partition.pdf import partition_pdf
from unstructured.partition.text import partition_text
from rag_modules.conversational_bot import Conversational_Bot
from tqdm import tqdm
import unstructured, os
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

def data_extracter(data, file_type, bot: Conversational_Bot = None):
    """
    Extracts text, images, and tables from structured and unstructured data.

    Args:
        data: Extracted file content (list of document elements or image data).
        file_type (str): Type of file ('pdf', 'text', 'image').
        bot (Conversational_Bot, optional): Conversational bot instance for summarization.

    Returns:
        tuple: Extracted texts, image summaries, and table summaries.
    """
    try:
        if file_type == 'pdf':
            if bot is None: ValueError("No bot provided.") 
            texts, tables, images = [], [], []
            
            for chunk in data:
                if isinstance(chunk, unstructured.documents.elements.Table):
                    tables.append(chunk)
                if isinstance(chunk, unstructured.documents.elements.CompositeElement):
                    texts.append(str(chunk))
                    chunk_elements = chunk.metadata.orig_elements
                    for element in chunk_elements:
                        if isinstance(element, unstructured.documents.elements.Image):
                            images.append(element.metadata.image_base64)
                            
            logger.info(f"Extracted: {len(texts)} texts, {len(images)} images, {len(tables)} tables")
            
            logger.info("Processing Images...")
            image_summaries = [bot.summarize_image(images[i]) for i in tqdm(range(len(images)))]
            
            logger.info("Processing Tables...")
            table_summaries = [bot.summarize_table(tables[i].metadata.text_as_html) for i in tqdm(range(len(tables)))]
            
            return texts, image_summaries, table_summaries
        elif file_type == 'text':
            texts = [str(chunk) for chunk in data if isinstance(chunk, unstructured.documents.elements.CompositeElement)]
            logger.info(f"Extracted: {len(texts)} texts")
            return texts
        elif file_type == 'image':
            image_summary = bot.summarize_image(data)
            logger.info(f"Extracted: {len(image_summary)} texts")
            return image_summary
    except Exception as e:
        logger.error(f"Error extracting data: {e}", exc_info=True)
        return None
    
def extract_pdf_data(file_path=None, file=None, bot: Conversational_Bot = None):
    """
    Extracts data from a PDF file.

    Args:
        file_path (str, optional): Path to the PDF file.
        file (file object, optional): File object of the PDF.
        bot (Conversational_Bot): Conversational bot instance for summarization.

    Returns:
        tuple: Extracted texts, image summaries, and table summaries.
    """
    try:
        if bot is None: ValueError("No bot provided.") 
        if file_path:
            logger.info(f"Processing PDF from file path: {file_path}")
            if not os.path.exists(file_path): raise FileNotFoundError("File does not exist: {file_path}")
            chunks = partition_pdf(
                filename=file_path,
                infer_table_structure=True,
                strategy="hi_res",
                extract_image_block_types=["Image"],
                extract_image_block_to_payload=True,
                chunking_strategy="by_title",
                max_characters=10000,
                combine_text_under_n_chars=2000,
                new_after_n_chars=6000
                )
        elif file:
            logger.info("Processing PDF from file object.")
            chunks = partition_pdf(
                file=file,
                infer_table_structure=True,
                strategy="hi_res",
                extract_image_block_types=["Image"],
                extract_image_block_to_payload=True,
                chunking_strategy="by_title",
                max_characters=10000,
                combine_text_under_n_chars=2000,
                new_after_n_chars=6000
                )
        else:
            raise ValueError("No file path / file provided.")
        
        return data_extracter(data=chunks, file_type='pdf', bot=bot)
    except Exception as e:
        logger.error(f"Error extracting PDF data: {e}")
        return None
    
def extract_txt_data(file_path=None, file=None):
    """
    Extracts text from a TXT file.
    
    Args:
        file_path (str, optional): Path to the TXT file.
        file (file object, optional): File object of the TXT.

    Returns:
        tuple: Extracted texts summaries.
    """
    try:
        if file_path:
            logger.info(f"Processing TXT file: {file_path}")
            if not os.path.exists(file_path): raise FileNotFoundError("File does not exist: {file_path}")
            chunks = partition_text(
                filename=file_path,
                max_characters=10000,
                combine_text_under_n_chars=2000,
                new_after_n_chars=6000
                )
        elif file:
            logger.info("Processing TXT from file object.")
            chunks = partition_text(
                file=file,
                max_characters=10000,
                combine_text_under_n_chars=2000,
                new_after_n_chars=6000
                )
        else:
            raise ValueError("No file path / file provided.")
        
        return data_extracter(data=chunks, file_type='text')
    except Exception as e:
        logger.error(f"Error extracting text data: {e}")
        return None
    
def extract_image_data(file_path=None, file=None, bot: Conversational_Bot = None):
    """
    Extracts data from an image file.
    
    Args:
        file_path (str, optional): Path to the image file.
        file (file object, optional): File object of the image.
        bot (Conversational_Bot): Conversational bot instance for summarization.

    Returns:
        tuple: Extracted image summaries summaries.
    """
    try:
        if bot is None: ValueError("No bot provided.") 
        
        if file_path:
            logger.info(f"Processing Image from file path: {file_path}")
            if not os.path.exists(file_path): raise FileNotFoundError("File does not exist: {file_path}")
            return data_extracter(data=file_path, file_type='image', bot=bot)
        elif file:
            logger.info("Processing Image from file object.")
            return data_extracter(data=file, file_type='image', bot=bot)
        else:
            raise ValueError("No file path / file provided.")
    except Exception as e:
        logger.error(f"Error extracting image data: {e}")
        return None