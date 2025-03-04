from fastapi import APIRouter, Depends, Form, UploadFile
from auth.dependencies import verify_token
from models.user import User
from models.session import create_new_session
from models.mongo_db import get_users_collection
from services.chat_service import chat_bot, delete_session_data, get_user_sessions
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
async def chat(session_id: str = Form(...), message: str = Form(...), image: UploadFile = None, rag_mode: str = Form(...)):
    """
    Endpoint to chat with AI in different modes.

    Args:
        session_id (str): The session ID for the chat.
        message (str): User's input message.
        image (UploadFile, optional): An image file uploaded by the user.
        rag_mode (str): Retrieval mode ('all', 'user', or 'no-rag').

    Returns:
        dict: AI-generated response message and session ID.
    """
    response, session = await chat_bot(session_id, message, image, rag_mode)
    
    return {"message": response.message.content, "session_id": session["session_id"]}

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a chat session by its session ID.

    Args:
        session_id (str): The ID of the session to delete.

    Returns:
        dict: Confirmation message after deletion.
    """
    await delete_session_data(session_id)

    return {"message": "Session deleted successfully"}