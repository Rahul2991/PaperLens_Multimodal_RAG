from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str
    
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    message: str
    username: str
    is_admin: bool
    
class RegisterResponse(BaseModel):
    message: str
    username: str