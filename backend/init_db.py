import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from models.agent import Base
from core.config import settings

def init_database():
    """Initialize the database and create tables"""
    # Create the database engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully!")
    
    # Test writing to the database
    try:
        with engine.connect() as conn:
            # Simple test insert
            result = conn.execute(text("SELECT 1"))
            print("Database connection test successful!")
    except Exception as e:
        print(f"Database connection test failed: {e}")

if __name__ == "__main__":
    init_database()