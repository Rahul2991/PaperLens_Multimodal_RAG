from rag_modules.conversational_bot import Conversational_Bot
from rag_modules.embed_data import EmbedData
from rag_modules.vector_db import QdrantVDB
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

def get_vector_db():
    """
    Initializes and returns an instance of QdrantVDB.

    Returns:
        QdrantVDB: An instance of the Qdrant vector database handler.
    """
    logger.info("Initializing Qdrant vector database instance.")
    return QdrantVDB()

def get_embed_data_obj():
    """
    Initializes and returns an instance of EmbedData.

    Returns:
        EmbedData: An instance of the embedding data handler.
    """
    logger.info("Initializing EmbedData instance.")
    return EmbedData()

# Initialize the conversational bot instance
logger.info("Initializing Conversational_Bot instance.")
bot = Conversational_Bot()