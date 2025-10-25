#!/usr/bin/env python3
"""
Migration script to add the total_messages column to the conversations table.
"""

from sqlalchemy import create_engine, text
from app.database import DATABASE_URL

def add_total_messages_column():
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            # Check if column exists first
            result = conn.execute(text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='conversations'
            """))

            if result.fetchone():
                # Check if column exists
                result = conn.execute(text("""
                    PRAGMA table_info(conversations)
                """))

                columns = [row[1] for row in result.fetchall()]
                if 'total_messages' not in columns:
                    print("Adding total_messages column to conversations table...")
                    # Add the column with default value 0
                    conn.execute(text("""
                        ALTER TABLE conversations ADD COLUMN total_messages INTEGER DEFAULT 0
                    """))
                    conn.commit()
                    print("✅ Successfully added total_messages column")
                else:
                    print("✅ total_messages column already exists")
            else:
                print("❌ conversations table does not exist")

    except Exception as e:
        print(f"❌ Error adding column: {e}")
        raise

if __name__ == "__main__":
    add_total_messages_column()
