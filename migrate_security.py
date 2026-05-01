"""
migrate_security.py — Ongeza columns mpya za security kwenye DB iliyopo
Run mara moja tu: python migrate_security.py
"""

import os
from dotenv import load_dotenv
load_dotenv()

from app import app, db
from sqlalchemy import text

def run_migration():
    with app.app_context():
        conn = db.engine.connect()
        
        migrations = [
            # Ongeza accepted_terms column kwenye users
            """
            DO $$ BEGIN
                ALTER TABLE users ADD COLUMN IF NOT EXISTS accepted_terms BOOLEAN DEFAULT FALSE;
            EXCEPTION WHEN duplicate_column THEN NULL;
            END $$;
            """,
            
            # Ongeza terms_accepted_at column kwenye users
            """
            DO $$ BEGIN
                ALTER TABLE users ADD COLUMN IF NOT EXISTS terms_accepted_at TIMESTAMP;
            EXCEPTION WHEN duplicate_column THEN NULL;
            END $$;
            """,
            
            # Unda banned_emails table kama haipo
            """
            CREATE TABLE IF NOT EXISTS banned_emails (
                id SERIAL PRIMARY KEY,
                email VARCHAR(120) UNIQUE,
                phone VARCHAR(20) UNIQUE,
                reason VARCHAR(300),
                banned_at TIMESTAMP DEFAULT NOW(),
                banned_by INTEGER REFERENCES users(id)
            );
            """,
            
            # Index kwa speed
            """
            CREATE INDEX IF NOT EXISTS idx_banned_email ON banned_emails(email);
            CREATE INDEX IF NOT EXISTS idx_banned_phone ON banned_emails(phone);
            """,
        ]
        
        for sql in migrations:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"✓ Migration OK")
            except Exception as e:
                print(f"✗ Migration error: {e}")
                conn.rollback()
        
        conn.close()
        print("\n✓ Migrations zote zimekamilika!")
        print("  Columns mpya: users.accepted_terms, users.terms_accepted_at")
        print("  Table mpya:   banned_emails")

if __name__ == "__main__":
    run_migration()
