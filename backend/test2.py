from models.sql_db import SessionLocal
from models.user import User

db = SessionLocal()  
print('----')
users_list = db.query(User).all()
print( [user.to_dict() for user in users_list])