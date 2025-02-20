from fastapi import HTTPException
from uuid import uuid4
from services.rag_service import bot
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

def find_session(user, session_id, set_history=True):
    """
    Finds an existing chat session for a user.

    Args:
        user (dict): The user data containing chat sessions.
        session_id (str): The ID of the chat session to find.
        set_history (bool, optional): Whether to set the bot's history to the session's chat history. Defaults to True.

    Returns:
        dict: The found chat session.

    Raises:
        HTTPException: If the session ID is invalid.
    """
    logger.info(f"Searching for session {session_id} for user {user.get('username', 'Unknown')}")
    
    session = next((s for s in user["chat_sessions"] if s["session_id"] == session_id), None)
    if not session:
        logger.error(f"Session ID {session_id} not found for user {user.get('username', 'Unknown')}")
        raise HTTPException(status_code=404, detail="Invalid session ID")
    if set_history: 
        logger.info(f"Setting bot history for session {session_id}")
        bot.set_history(session['bot_chat_history'].copy())
    
    logger.info(f"Session {session_id} retrieved successfully")
    return session

def create_new_session(user):
    """
    Creates a new chat session for a user.

    Args:
        user (dict): The user data to append the new session to.

    Returns:
        dict: The newly created chat session.
    """
    logger.info(f"Creating a new chat session for user {user.get('username', 'Unknown')}")

    sys_inst = {
        "role": "system", 
        "content": "You are an expert in the field of AI Research and current AI Trends."
        }
    session = {
        "session_id": str(uuid4()), # Generate a unique session ID
        "messages": [], # Initialize an empty message list
        "bot_chat_history": [sys_inst] # Store system instructions as the first message
        }
    user["chat_sessions"].append(session) # Append the new session to the user's chat history
    bot.set_history([]) # Reset bot history for the new session
    
    logger.info(f"New session created with ID {session['session_id']} for user {user.get('username', 'Unknown')}")
    return session