from pydantic import BaseModel
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

# User registration model for input validation
class UserRegister(BaseModel):
    """
    Pydantic model for user registration data.

    Attributes:
        username: The username of the user.
        password: The password of the user.
    """
    username: str
    password: str

    def __init__(self, **kwargs):
        """
        Initializes the UserRegister model.

        Args:
            kwargs: keyword arguments containing username and password.
        """
        super().__init__(**kwargs)
        logger.info(f"User registration initialized for: {self.username}")

# User login model for input validation
class UserLogin(BaseModel):
    """
    Pydantic model for user login data.

    Attributes:
        username: The username of the user attempting to login.
        password: The password of the user attempting to login.
    """
    username: str
    password: str

    def __init__(self, **kwargs):
        """
        Initializes the UserLogin model.

        Args:
            kwargs: keyword arguments containing username and password.
        """
        super().__init__(**kwargs)
        logger.info(f"Login attempt initialized for: {self.username}")

# Response model for login, includes JWT access token and user info
class LoginResponse(BaseModel):
    """
    Pydantic model for the response data after a successful login.

    Attributes:
        access_token: The JWT token issued for the session.
        token_type: The type of token (usually "bearer").
        message: A message indicating the status of the login.
        username: The username of the logged-in user.
        is_admin: A flag indicating if the user is an admin.
    """
    access_token: str
    token_type: str
    message: str
    username: str
    is_admin: bool

    def __init__(self, **kwargs):
        """
        Initializes the LoginResponse model.

        Args:
            kwargs: keyword arguments containing access_token, token_type, message, username, and is_admin.
        """
        super().__init__(**kwargs)
        logger.info(f"Login response prepared for user: {self.username}")

# Response model for user registration, returns a confirmation message and username
class RegisterResponse(BaseModel):
    """
    Pydantic model for the response data after a successful registration.

    Attributes:
        message: A confirmation message regarding the registration status.
        username: The username of the newly registered user.
    """
    message: str
    username: str

    def __init__(self, **kwargs):
        """
        Initializes the RegisterResponse model.

        Args:
            kwargs: keyword arguments containing message and username.
        """
        super().__init__(**kwargs)
        logger.info(f"Registration response prepared for user: {self.username}")