"""
Database migration to add Credential table for secure credential storage
"""
from sqlalchemy import text
from core.database import engine


def upgrade():
    """Create the credentials table"""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS credentials (
                id SERIAL PRIMARY KEY,
                credential_id VARCHAR UNIQUE NOT NULL,
                name VARCHAR NOT NULL,
                type VARCHAR NOT NULL,
                data JSONB NOT NULL,
                tenant_id VARCHAR,
                created_by VARCHAR,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE
            );
        """))
        
        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_credentials_credential_id ON credentials(credential_id);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_credentials_name ON credentials(name);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_credentials_tenant_id ON credentials(tenant_id);
        """))
        
        conn.commit()
        print("✅ Credentials table created successfully")


def downgrade():
    """Drop the credentials table"""
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS credentials;"))
        conn.commit()
        print("✅ Credentials table dropped successfully")


if __name__ == "__main__":
    print("Running credentials migration...")
    upgrade()
