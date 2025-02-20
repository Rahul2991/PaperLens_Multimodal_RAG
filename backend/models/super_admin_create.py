from config import logger
from sqlalchemy.orm import Session
from auth.security import hash_password
from models.user import User

def create_super_admin(username: str, password: str, db: Session):
    """
    Creates a super admin user in the database.

    Args:
        username (str): The username for the admin account.
        password (str): The raw password to be hashed and stored.
        db (Session): The database session used for committing changes.

    Returns:
        None
    """
    try:
        logger.info(f"Creating super admin with username: {username}")
        
        # Hash the password before storing it in the database
        hashed_pw = hash_password(password)
        
        # Create a new admin user instance
        admin = User(username=username, hashed_password=hashed_pw, is_admin=1)
        
        # Add and commit the admin user to the database
        db.add(admin)
        db.commit()
        
        logger.info("Super admin created successfully")
    except Exception as e:
        logger.error(f"Error creating super admin: {e}")
    finally:
        db.close()
        logger.info("Database session closed")
        
if __name__ == '__main__':
    # To create a super admin, uncomment and provide username/password
    # create_super_admin('admin_username', 'admin_password', SessionLocal())
    ...