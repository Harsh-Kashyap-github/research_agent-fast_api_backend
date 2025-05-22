from sqlalchemy import Column, Integer, String, UUID, DateTime, ForeignKey
import uuid
from database import Base


class Users(Base):
    __tablename__ = 'users'
    id=Column(Integer, primary_key=True, autoincrement=True)
    username=Column(String,index=True,unique=True)
    hashed_password=Column(String,index=True)

class Prompts(Base):
    __tablename__ = 'prompts'
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id=Column(String,ForeignKey('users.username'),nullable=False)
    query=Column(String,index=True)
    casual_response=Column(String)
    formal_response=Column(String)
    created_at = Column(DateTime, index=True)