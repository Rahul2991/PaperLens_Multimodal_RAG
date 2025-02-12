from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.sql_db import get_db, Base, engine
from models.user import User
from auth.dependencies import admin_only
from routes import auth, chat, admin, user
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict


app = FastAPI()
Base.metadata.create_all(bind=engine)

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
    
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(user.router, prefix="/user", tags=["user"])

class ChatRequest(BaseModel):
    msg: str
    
class MongoUser(BaseModel):
    username: str
    chat_sessions: List[Dict] = []

@app.get("/")
def home():
    return {"message": "Welcome to Multimodal RAG!"}