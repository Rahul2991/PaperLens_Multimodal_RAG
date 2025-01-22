from datetime import timedelta, datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from auth import create_access_token, verify_token
from bot import Conversational_Bot
from models import User, get_db, hash_password, verify_password
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List, Dict
from uuid import uuid4
import os

load_dotenv()

app = FastAPI()

MONGO_URI = os.getenv('MONGO_URI')
client = AsyncIOMotorClient(MONGO_URI)
mongo_db = client["chat_app"]
users_collection = mongo_db["users"]

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str
    
class ChatRequest(BaseModel):
    msg: str
    
class MongoUser(BaseModel):
    username: str
    chat_sessions: List[Dict] = []
    
user_sessions_cache = {}

def initialize_bot():
    system_message = "You are an expert in the field of AI Research and current AI Trends."
    bot_instance = Conversational_Bot(system_message)
    return bot_instance

bot = initialize_bot()

@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    hashed_pw = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=1800))
    return {"access_token": access_token, "token_type": "bearer", "message": "Login successful", "username": user.username}

@app.get("/chat")
def chat(user: User = Depends(verify_token)):
    return {"message": f"Welcome to the chat, {user.username}!"}

async def get_user_sessions(current_user: User = Depends(verify_token)):
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

def find_session(user, session_id, set_history=True):
    session = next((s for s in user["chat_sessions"] if s["session_id"] == session_id), None)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session ID")
    else:
        if set_history: bot.set_history(session['messages'])
    return session

def create_new_session(user):
    session = {"session_id": str(uuid4()), "messages": []}
    user["chat_sessions"].append(session)
    bot.set_history([])
    return session

@app.get("/sessions")
async def list_sessions(user: dict = Depends(get_user_sessions)):
    return {"sessions": [{"session_id": s["session_id"], "messages_count": len(s["messages"]), "messages": s["messages"]} for s in user["chat_sessions"]]}

@app.post("/create_session")
async def create_session(user: dict = Depends(get_user_sessions)):
    new_session = create_new_session(user)
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$push": {"chat_sessions": new_session}}
    )
    return {"session_id": new_session["session_id"]}

@app.post("/chat_ai")
async def chat(session_id: str = Form(...), message: str = Form(...), image: UploadFile = None, user: dict = Depends(get_user_sessions)):
    print('session_id', session_id)
    session = find_session(user, session_id) if session_id else create_session(user)
    
    image_content = None
    if image:
        image_content = await image.read()
    response = bot.generate(message, image_content)
    
    session["messages"] = bot.get_history()
    
    user_sessions_cache[user["username"]] = user
    
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"chat_sessions": user["chat_sessions"]}}
    )

    return {"message": response.message.content, "session_id": session["session_id"]}

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user: dict = Depends(get_user_sessions)):
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