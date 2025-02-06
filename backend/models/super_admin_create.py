from sqlalchemy.orm import Session
from auth.security import hash_password
from models.user import User

def create_super_admin(username: str, password: str, db: Session):
    try:
        hashed_pw = hash_password(password)
        admin = User(username=username, hashed_password=hashed_pw, is_admin=1)
        db.add(admin)
        db.commit()
        print("Admin created successfully")
    except Exception as e:
        print(f"Error creating admin: {e}")
    finally:
        db.close()
        
if __name__ == '__main__':
    # create_super_admin('', '', SessionLocal())
    ...