from fastapi import HTTPException
from uuid import uuid4
from services.rag_service import bot

def find_session(user, session_id, set_history=True):
    session = next((s for s in user["chat_sessions"] if s["session_id"] == session_id), None)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session ID")
    else:
        if set_history: bot.set_history(session['bot_chat_history'].copy())
    return session

def create_new_session(user):
    sys_inst = {"role": "system", "content": "You are an expert in the field of AI Research and current AI Trends."}
    session = {"session_id": str(uuid4()), "messages": [], "bot_chat_history": [sys_inst]}
    user["chat_sessions"].append(session)
    bot.set_history([])
    return session