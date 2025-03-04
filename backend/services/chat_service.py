from fastapi import Depends, UploadFile, HTTPException, status
from models.user import User
from auth.dependencies import verify_token
from motor.motor_asyncio import AsyncIOMotorCollection
from models.mongo_db import get_users_collection
from services.rag_service import bot, get_embed_data_obj, get_vector_db
from rag_modules.vector_db import QdrantVDB
from models.session import create_new_session, find_session
from rag_modules.rag import RAG
from rag_modules.rag_retriever import Retriever
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
    if username not in user_sessions_cache or not isinstance(user_sessions_cache[username], dict) or 'chat_sessions' not in user_sessions_cache[username].keys():
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

async def chat_bot(
    session_id: str, 
    message: str, 
    image: UploadFile = None,  
    rag_mode: str = 'no-rag', 
    user: dict = Depends(get_user_sessions), 
    users_collection = Depends(get_users_collection),
    current_user: User = Depends(verify_token),
    embed_data = Depends(get_embed_data_obj),
    vector_db: QdrantVDB = Depends(get_vector_db)):
    """
    Process user messages using AI and return responses.

    Args:
        session_id (str): The session ID for the chat.
        message (str): User's input message.
        image (UploadFile, optional): An image file uploaded by the user.
        rag_mode (str): Retrieval mode ('all', 'user', or 'no-rag').
        user (dict): The authenticated user's session data.
        users_collection: MongoDB collection for user data.
        current_user (User): The authenticated user.
        embed_data: Embedding model instance.
        vector_db (QdrantVDB): Vector database instance.

    Returns:
        dict: AI-generated response message and session ID.
    """
    try:
        logger.info(f"User {current_user.username} sent a message in session {session_id}. RAG Mode: {rag_mode}")
        
        # Find or create a session
        session = create_new_session(user) if (session_id == 'null' or session_id == None) else find_session(user, session_id)
        
        # Process image input
        image_content = None
        if image:
            image_content = await image.read()

        # Add user message to the session history
        session["messages"].extend([{'role': 'user', 'text': message}])
        
        # AI Response generation based on RAG mode
        if rag_mode == "all":
            vector_db.create_or_set_collection(collection_name='multimodal_rag_admin_collection')
            retriever = Retriever(vector_db=vector_db, embeddata=embed_data)
            rag_client = RAG(retriever=retriever, bot=bot)
            response = rag_client.query(message, image_content)
        elif rag_mode == "user":
            user_folder_name = current_user.username + '_' + str(current_user.id)
            vector_db.create_or_set_collection(collection_name='multimodal_rag_' + user_folder_name)
            retriever = Retriever(vector_db=vector_db, embeddata=embed_data)
            rag_client = RAG(retriever=retriever, bot=bot)
            response = rag_client.query(message, image_content)
        else:
            response = bot.generate(message, image_content)
        
        # Add bot response to the session history
        session["messages"].extend([{'role': 'bot', 'text': response.message.content}])
        session["bot_chat_history"] = bot.get_history()
        
        # Cache update
        user_sessions_cache[user["username"]] = user
        
        # Save session updates to MongoDB
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"chat_sessions": user["chat_sessions"]}}
        )
        
        logger.info(f"AI response sent to user {current_user.username} in session {session['session_id']}.")
        return response, session
    except Exception as e:
        logger.error(f"Error processing user message in session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing user message in session {session_id}: {str(e)}"
        )
    
async def delete_session_data(session_id: str, user: dict = Depends(get_user_sessions), users_collection: AsyncIOMotorCollection = Depends(get_users_collection)):
    """
    Delete a chat session by its session ID.

    Args:
        session_id (str): The ID of the session to delete.
        user (dict): The authenticated user's session data.
        users_collection (AsyncIOMotorCollection): MongoDB collection for user data.

    Returns:
        dict: Confirmation message after deletion.
    """
    logger.info(f"Deleting session {session_id} for user {user['username']}.")
    
    # Filter out the session to be deleted
    user_sessions = user.get("chat_sessions", [])
    updated_sessions = [session for session in user_sessions if session["session_id"] != session_id]

    # Update the user document in MongoDB
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"chat_sessions": updated_sessions}}
    )

    # Update the cache
    user["chat_sessions"] = updated_sessions
    user_sessions_cache[user["username"]] = user
    
    logger.info(f"Session {session_id} deleted successfully for user {user['username']}.")