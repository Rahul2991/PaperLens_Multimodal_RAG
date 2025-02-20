from sqlalchemy import Column, Integer, String, Boolean
from models.sql_db import Base
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

class User(Base):
    """
    Database model representing a user.

    Attributes:
        - id (int): Unique identifier for the user.
        - username (str): Unique username for the user.
        - hashed_password (str): Hashed password for authentication.
        - is_admin (bool): Indicates whether the user has admin privileges.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    def to_dict(self):
        """
        Convert the user object into a dictionary format.

        Returns:
            dict: A dictionary representation of the user object.
        """
        user_dict = {
            "id": self.id,
            "username": self.username,
            "is_admin": self.is_admin
        }
        logger.debug(f"Converting User object to dictionary: {user_dict}")
        return user_dict