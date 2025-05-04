from sqlmodel import SQLModel, Session, create_engine
from loguru import logger
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL, 
    echo=settings.DEBUG,
    pool_pre_ping=True
)

def init_db() -> None:
    logger.info("Initializing database...")
    try:
        SQLModel.metadata.create_all(engine)
        logger.success("Database tables created successfully!")
        
        # Run migrations for existing tables
        from app.db.migrations import run_migrations
        if run_migrations():
            logger.info("Database migrations applied successfully!")
            
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_session():
    with Session(engine) as session:
        yield session