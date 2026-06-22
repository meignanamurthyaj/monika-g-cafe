# sqlalchemy imports - used to create the database engine, session, and base class for models
# config import settings - used to get the database URL from the environment variables
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

# create the database engine using the database URL from the environment variables
# create the sessionmaker, which will be used to create database sessions
# create the base class for models, which will be used to define the database tables
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# create a function that will be used to get a database session, which will be used in the API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()