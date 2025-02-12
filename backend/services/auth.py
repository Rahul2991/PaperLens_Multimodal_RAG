from sqlalchemy.orm import Session
from schemas.user import UserRegister, UserLogin
from auth.security import hash_password, verify_password, create_access_token
from datetime import timedelta
from models.user import User
from fastapi import HTTPException, status

def create_user(user: UserRegister, db: Session) -> User:
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
    return new_user

def authenticate_user(user: UserLogin, db: Session):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return db_user

def create_access_token_for_user(user: UserLogin, is_admin: bool) -> str:
    return create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=60) if is_admin else None)