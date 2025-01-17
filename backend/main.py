from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from auth import create_access_token, verify_token
from bot import Conversational_Bot
from models import User, get_db, hash_password, verify_password
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

def initialize_bot():
    system_message = "You are an expert in the field of AI Research and current AI Trends."
    return Conversational_Bot(system_message)
        
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
def chat(user: User = Depends(verify_token), ):
    return {"message": f"Welcome to the chat, {user.username}!"}

@app.post("/chat_ai")
def chat(request: ChatRequest, user: User = Depends(verify_token), bot: Conversational_Bot = Depends(initialize_bot)):
    response = bot.generate(request.msg)
    return {"message": f"{response.message.content}!"}