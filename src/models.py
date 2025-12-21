from database import Base
# from src.database import Base
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean,DateTime,ForeignKey

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at= Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)) 


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String,nullable=False)
    description = Column(String,nullable=False)
    priority = Column(Integer,nullable=False)
    complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at= Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)) 
    owner_id = Column(Integer, ForeignKey("users.id"))