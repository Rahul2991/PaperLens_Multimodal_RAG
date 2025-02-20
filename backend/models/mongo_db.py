from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

# MongoDB connection URI from the configuration
MONGO_URI = Config.MONGO_URI

# Initialize an asynchronous MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
mongo_db_client = client["chat_app"]

logger.info("Connected to MongoDB database: chat_app")

def get_users_collection():
    """
    Retrieves the 'users' collection from the MongoDB database.

    Returns:
        motor.motor_asyncio.AsyncIOMotorCollection: The users collection.
    """
    logger.info("Fetching 'users' collection from MongoDB.")
    return mongo_db_client["users"]

def get_files_collection():
    """
    Retrieves the 'files' collection from the MongoDB database.

    Returns:
        motor.motor_asyncio.AsyncIOMotorCollection: The files collection.
    """
    logger.info("Fetching 'files' collection from MongoDB.")
    return mongo_db_client["files"]
