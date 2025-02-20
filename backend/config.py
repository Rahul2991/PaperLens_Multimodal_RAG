from dotenv import load_dotenv
import os, logging
from datetime import datetime

# Load environment variables from a .env file
load_dotenv()

# Ensure logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"Multimodal_rag_bot_{datetime.now().strftime('%y_%m_%d_%H_%M_%S_%f')}.log")

# Configure logging with a detailed format and log file
logFormat = '%(asctime)s | %(name)s | %(module)s %(filename)s:%(lineno)d %(funcName)s | %(levelname)s | [PID: %(process)d] [Thread: %(threadName)s] | %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=logFormat,
    handlers=[
        logging.FileHandler(LOG_FILE),  # Log to a file in logs directory
        logging.StreamHandler()  # Log to console
    ]
)
logger = logging.getLogger("Multimodal_rag_bot")

class Config:
    """
    Configuration class to manage environment variables and directory setup.
    """
    DATABASE_URL = os.getenv("SQL_DATABASE_URL")
    MONGO_URI = os.getenv('MONGO_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    ACCESS_TOKEN_EXPIRE_MINUTES = 1800 # 1800 minutes expiration for access tokens
    ALGORITHM = "HS256" # Algorithm used for encoding JWT tokens
    ADMIN_UPLOAD_FILE_LOCATION = "uploads/admin"
    USER_UPLOAD_FILE_LOCATION = "uploads/users"
    TEMP_DIR = "temp"
    
    @staticmethod
    def ensure_directories():
        """
        Ensures that required directories exist, creating them if necessary.
        """
        directories = [
            Config.ADMIN_UPLOAD_FILE_LOCATION,
            Config.USER_UPLOAD_FILE_LOCATION,
            Config.TEMP_DIR,
            LOG_DIR
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Ensured directory exists: {directory}")
            except Exception as e:
                logger.error(f"Error creating directory {directory}: {e}")

# Ensure necessary directories exist during initialization
Config.ensure_directories()