from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True)
    nickname = Column(String)
    avatar = Column(String)
    description = Column(String)
    follows = Column(Integer)
    fans = Column(Integer)
    likes = Column(Integer)
    last_updated = Column(DateTime, default=datetime.now)
    raw_info = Column(JSON)  # 存储原始用户信息

class Note(Base):
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True)
    note_id = Column(String, unique=True)
    user_id = Column(String)
    title = Column(String)
    type = Column(String)
    likes = Column(Integer)
    user_nickname = Column(String)
    user_avatar = Column(String)
    cover_url = Column(String)
    cover_width = Column(Integer)
    cover_height = Column(Integer)
    created_at = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.now)
    raw_info = Column(JSON)  # 存储原始笔记信息

def init_db():
    engine = create_engine('sqlite:///xhs_monitor.db')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)() 