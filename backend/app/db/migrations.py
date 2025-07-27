from sqlalchemy import text
from app.db.session import engine

def run_migrations():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='user' AND column_name='updated_at'
        """))
        
        if not result.fetchone():
            conn.execute(text("""
                ALTER TABLE "user" ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE 
                DEFAULT CURRENT_TIMESTAMP NOT NULL
            """))
            conn.commit()
            return True
    return False