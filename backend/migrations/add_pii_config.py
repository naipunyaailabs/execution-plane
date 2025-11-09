"""
Database Migration: Add PII Configuration Column

This migration adds the pii_config JSON column to the agents table
to store PII filtering configurations including allowed types,
custom categories, and filtering strategies.

Run with: python migrations/add_pii_config.py
"""

import sys
import os

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from core.config import settings


def run_migration():
    """Add pii_config column to agents table"""
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("PRAGMA table_info(agents)"))
            columns = [row[1] for row in result]
            
            if 'pii_config' in columns:
                print("✓ Column 'pii_config' already exists in agents table")
                return True
            
            # Add the column
            print("Adding pii_config column to agents table...")
            conn.execute(text("ALTER TABLE agents ADD COLUMN pii_config JSON"))
            conn.commit()
            
            print("✓ Successfully added pii_config column to agents table")
            return True
            
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False


def verify_migration():
    """Verify the migration was successful"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(agents)"))
            columns = [row[1] for row in result]
            
            if 'pii_config' in columns:
                print("✓ Migration verified: pii_config column exists")
                return True
            else:
                print("✗ Verification failed: pii_config column not found")
                return False
                
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PII Configuration Migration")
    print("=" * 60)
    
    success = run_migration()
    
    if success:
        verify_migration()
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Migration failed!")
        print("=" * 60)
        sys.exit(1)
