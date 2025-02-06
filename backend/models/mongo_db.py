from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

MONGO_URI = Config.MONGO_URI
client = AsyncIOMotorClient(MONGO_URI)
mongo_db_client = client["chat_app"]

def get_users_collection():
    return mongo_db_client["users"]

def get_files_collection():
    return mongo_db_client["files"]
