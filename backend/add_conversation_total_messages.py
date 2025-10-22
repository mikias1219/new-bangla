#!/usr/bin/env python3
"""
Migration script to add total_messages column to conversations table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database import DATABASE_URL

def add_total_messages_column():
    """Add total_messages column to conversations table"""
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'conversations'
                AND column_name = 'total_messages'
            """))

            if result.fetchone():
                print("✅ total_messages column already exists")
                return True

            # Add the column
            conn.execute(text("ALTER TABLE conversations ADD COLUMN total_messages INTEGER DEFAULT 0"))
            conn.commit()

            print("✅ Successfully added total_messages column to conversations table")
            return True

    except Exception as e:
        print(f"❌ Error adding total_messages column: {e}")
        return False

if __name__ == "__main__":
    success = add_total_messages_column()
    sys.exit(0 if success else 1)
