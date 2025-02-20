from fastapi import Depends
from models.user import User
from auth.dependencies import verify_token
from models.mongo_db import get_users_collection
from cache import user_sessions_cache
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

async def get_user_sessions(current_user: User = Depends(verify_token), users_collection = Depends(get_users_collection)):
    """
    Retrieves or creates a user's chat session data from the database. If the user does not exist in the database, a new entry is created.
    Updates the in-memory cache (`user_sessions_cache`) with the user's session data.

    Args:
        current_user (User): The authenticated user retrieved via token verification.
        users_collection: The MongoDB collection for storing user data.

    Returns:
        dict: The user session data containing username and chat sessions.
    """
    username = current_user.username
    logger.info(f"Fetching session data for user: {username}")
    
    # Check if user session exists in cache
    if username not in user_sessions_cache:
        logger.debug(f"User {username} not found in cache. Fetching from database.")
        
        # Retrieve user from MongoDB
        user = await users_collection.find_one({"username": username})
        
        if not user:
            logger.info(f"User {username} does not exist in the database. Creating a new entry.")
            
            # Create a new user if they don't exist
            user = {"username": username, "chat_sessions": []}
            result = await users_collection.insert_one(user)
            user["_id"] = result.inserted_id
            
            logger.info(f"New user {username} successfully created in the database.")
        
        # Store user session in cache
        user_sessions_cache[username] = user
        logger.debug(f"User {username} session cached successfully.")
        
    return user_sessions_cache[username]
