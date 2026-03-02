from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi import Depends

DATA_BASE_URL = "postgresql+psycopg2://postgres:18566429@localhost:5432/fitness_platform"

engine = create_engine(DATA_BASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


#Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()