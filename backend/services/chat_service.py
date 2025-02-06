from fastapi import Depends
from models.user import User
from auth.dependencies import verify_token
from models.mongo_db import get_users_collection
from cache import user_sessions_cache

async def get_user_sessions(current_user: User = Depends(verify_token), users_collection = Depends(get_users_collection)):
    username = current_user.username
    if username not in user_sessions_cache:
        user = await users_collection.find_one({"username": username})
        if not user:
            # Create a new user if they don't exist
            user = {"username": username, "chat_sessions": []}
            result = await users_collection.insert_one(user)
            user["_id"] = result.inserted_id
        user_sessions_cache[username] = user
    return user_sessions_cache[username]
