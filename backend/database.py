# database.py
import os
from sqlmodel import SQLModel, create_engine, Session
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")  
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "zkp_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

logger.debug(f"Connecting to database at {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")

engine = create_engine(DATABASE_URL)

def init_db():
    """Initializes the database by creating all tables."""
    logger.info("Attempting to create database tables if they don't exist...")
    try:
        SQLModel.metadata.create_all(engine)
        logger.success("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

def get_session():
    """FastAPI dependency that provides a database session."""
    with Session(engine) as session:
        yield session