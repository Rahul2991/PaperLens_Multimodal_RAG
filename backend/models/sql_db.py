from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

# SQL connection URI from the configuration
SQL_URI = Config.DATABASE_URL

# Create an SQLite database engine
engine = create_engine(SQL_URI)

# Create a session factory bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the base class for ORM models
Base = declarative_base()

def get_db():
    """
    Dependency function to get a database session.

    Yields:
        Session: A SQLAlchemy database session.

    Ensures that the session is properly closed after use.
    """
    db = SessionLocal()
    try:
        logger.info("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
    finally:
        db.close()
        logger.info("Database session closed")