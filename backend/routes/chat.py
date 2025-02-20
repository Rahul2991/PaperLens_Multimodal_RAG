from fastapi import APIRouter, Depends, Form, UploadFile
from auth.dependencies import verify_token
from rag_modules.vector_db import QdrantVDB
from rag_modules.rag_retriever import Retriever
from rag_modules.rag import RAG
from models.user import User
from models.session import create_new_session, find_session
from models.mongo_db import get_users_collection
from services.chat_service import get_user_sessions
from services.rag_service import bot, get_embed_data_obj, get_vector_db
from cache import user_sessions_cache
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

# Create a FastAPI router for chat-related endpoints
router = APIRouter()

@router.get("/chat")
def chat(user: User = Depends(verify_token)):
    """
    Endpoint to return a welcome message for authenticated users.

    Args:
        user (User): The authenticated user.

    Returns:
        dict: A welcome message.
    """
    logger.info(f"User {user.username} accessed the chat endpoint.")
    return {"message": f"Welcome to the chat, {user.username}!"}

@router.get("/sessions")
async def list_sessions(user: dict = Depends(get_user_sessions)):
    """
    Retrieve a list of all chat sessions for the authenticated user.

    Args:
        user (dict): The authenticated user's session data.

    Returns:
        dict: List of chat sessions including session IDs and message counts.
    """
    logger.info(f"Listing chat sessions for user: {user['username']}.")
    return {"sessions": [{"session_id": s["session_id"], "messages_count": len(s["messages"]), "messages": s["messages"]} for s in user["chat_sessions"]]}

@router.post("/create_session")
async def create_session(user: dict = Depends(get_user_sessions), users_collection = Depends(get_users_collection)):
    """
    Create a new chat session for the authenticated user.

    Args:
        user (dict): The authenticated user's session data.
        users_collection: MongoDB collection for user data.

    Returns:
        dict: The newly created session ID.
    """
    logger.info(f"Creating a new chat session for user: {user['username']}.")
    
    new_session = create_new_session(user)
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$push": {"chat_sessions": new_session}}
    )
    return {"session_id": new_session["session_id"]}

@router.post("/chat_ai")
async def chat(
    session_id: str = Form(...), 
    message: str = Form(...), 
    image: UploadFile = None, 
    rag_mode: str = Form(...),
    user: dict = Depends(get_user_sessions), 
    users_collection = Depends(get_users_collection),
    current_user: User = Depends(verify_token),
    embed_data = Depends(get_embed_data_obj),
    vector_db: QdrantVDB = Depends(get_vector_db)
    ):
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
    
    return {"message": response.message.content, "session_id": session["session_id"]}

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user: dict = Depends(get_user_sessions), users_collection = Depends(get_users_collection)):
    """
    Delete a chat session by its session ID.

    Args:
        session_id (str): The ID of the session to delete.
        user (dict): The authenticated user's session data.
        users_collection: MongoDB collection for user data.

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

    return {"message": "Session deleted successfully"}