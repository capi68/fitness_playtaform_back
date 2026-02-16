from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi import Depends

DATA_BASE_URL = "sqlite:///./fitness_proyect.db"

engine = create_engine(
    DATA_BASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


#Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()