from fastapi import APIRouter, Depends, Form, UploadFile
from auth.dependencies import verify_token
from models.user import User
from models.session import create_new_session, find_session
from models.mongo_db import get_users_collection
from services.chat_service import get_user_sessions
from services.rag_service import bot, get_embed_data_obj, get_vector_db
from cache import user_sessions_cache

router = APIRouter()

@router.get("/chat")
def chat(user: User = Depends(verify_token)):
    return {"message": f"Welcome to the chat, {user.username}!"}

@router.get("/sessions")
async def list_sessions(user: dict = Depends(get_user_sessions)):
    return {"sessions": [{"session_id": s["session_id"], "messages_count": len(s["messages"]), "messages": s["messages"]} for s in user["chat_sessions"]]}

@router.post("/create_session")
async def create_session(user: dict = Depends(get_user_sessions), users_collection = Depends(get_users_collection)):
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
    user: dict = Depends(get_user_sessions), 
    users_collection = Depends(get_users_collection)
    ):
    print('session_id', session_id)
    session = create_new_session(user) if (session_id == 'null' or session_id == None) else find_session(user, session_id)
    
    image_content = None
    if image:
        image_content = await image.read()
    
    session["messages"].extend({'role': 'user', 'text': message})
    response = bot.generate(message, image_content)
    session["messages"].extend({'role': 'bot', 'text': response.message.content})
    session["bot_chat_history"] = bot.get_history()
    user_sessions_cache[user["username"]] = user
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"chat_sessions": user["chat_sessions"]}}
    )

    return {"message": response.message.content, "session_id": session["session_id"]}

@router.post("/chat_rag_ai")
async def chat(
    session_id: str = Form(...), 
    message: str = Form(...), 
    image: UploadFile = None, 
    user: dict = Depends(get_user_sessions), 
    users_collection = Depends(get_users_collection),
    embed_data = Depends(get_embed_data_obj),
    vector_db = Depends(get_vector_db)
    ):
    print('session_id', session_id)
    session = create_new_session(user) if (session_id == 'null' or session_id == None) else find_session(user, session_id)
    
    image_content = None
    if image:
        image_content = await image.read()
    
    session["messages"].extend({'role': 'user', 'text': message})
    response = bot.generate(message, image_content)
    session["messages"].extend({'role': 'bot', 'text': response.message.content})
    session["bot_chat_history"] = bot.get_history()
    user_sessions_cache[user["username"]] = user
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"chat_sessions": user["chat_sessions"]}}
    )

    return {"message": response.message.content, "session_id": session["session_id"]}

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user: dict = Depends(get_user_sessions), users_collection = Depends(get_users_collection)):
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

    return {"message": "Session deleted successfully"}