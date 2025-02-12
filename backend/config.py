from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("SQL_DATABASE_URL")
    MONGO_URI = os.getenv('MONGO_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    ACCESS_TOKEN_EXPIRE_MINUTES = 1800
    ALGORITHM = "HS256"
    ADMIN_UPLOAD_FILE_LOCATION = "uploads/admin"
    USER_UPLOAD_FILE_LOCATION = "uploads/users"
    TEMP_DIR = "temp"
    
    @staticmethod
    def ensure_directories():
        os.makedirs(Config.ADMIN_UPLOAD_FILE_LOCATION, exist_ok=True)
        os.makedirs(Config.USER_UPLOAD_FILE_LOCATION, exist_ok=True)
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
        
Config.ensure_directories()