from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    email = Column(String(255), nullable=False)
    task = Column(String(255), nullable=False)
    round = Column(Integer, nullable=False)
    nonce = Column(String(255), nullable=False, unique=True)
    brief = Column(Text, nullable=False)
    attachments = Column(Text)  # JSON string
    checks = Column(Text)  # JSON string
    evaluation_url = Column(String(500), nullable=False)
    endpoint = Column(String(500), nullable=False)
    statuscode = Column(Integer)
    secret = Column(String(255), nullable=False)

class Repo(Base):
    __tablename__ = 'repos'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    email = Column(String(255), nullable=False)
    task = Column(String(255), nullable=False)
    round = Column(Integer, nullable=False)
    nonce = Column(String(255), nullable=False)
    repo_url = Column(String(500), nullable=False)
    commit_sha = Column(String(255), nullable=False)
    pages_url = Column(String(500), nullable=False)

class Result(Base):
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    email = Column(String(255), nullable=False)
    task = Column(String(255), nullable=False)
    round = Column(Integer, nullable=False)
    repo_url = Column(String(500), nullable=False)
    commit_sha = Column(String(255), nullable=False)
    pages_url = Column(String(500), nullable=False)
    check = Column(String(500), nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(Text)
    logs = Column(Text)

# Database session management
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

