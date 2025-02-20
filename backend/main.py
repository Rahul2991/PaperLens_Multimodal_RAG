from fastapi import FastAPI
from pydantic import BaseModel
from models.sql_db import Base, engine
from routes import auth, chat, admin, user
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import logging

# Configure logger for the FastAPI application
logger = logging.getLogger("Multimodal_rag_bot")

# Initialize FastAPI app
app = FastAPI()

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)
logger.info("Database tables created (if not already present).")

# Allowed origins for CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost:3000", # Frontend URL
]

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Allow specified origins
    allow_credentials=True, # Allow credentials (cookies, headers)
    allow_methods=["*"], # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)

# Include route modules with respective prefixes and tags
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(user.router, prefix="/user", tags=["user"])

# Log the successful inclusion of routers
logger.info("Routers for auth, chat, admin, and user have been registered.")

class ChatRequest(BaseModel):
    """
    Request model for chat messages.

    Attributes:
        msg (str): The input message from the user.
    """
    msg: str
    
class MongoUser(BaseModel):
    """
    Pydantic model for storing user data in MongoDB.

    Attributes:
        username (str): The user's name.
        chat_sessions (List[Dict]): List of chat session data.
    """
    username: str
    chat_sessions: List[Dict] = []

@app.get("/")
def home():
    """
    Root endpoint for the API.

    Returns:
        dict: A welcome message.
    """
    return {"message": "Welcome to Multimodal RAG!"}