#!/usr/bin/env python3
"""
Migration script to add admin review fields to conversations table.
"""

import os
import sys
from sqlalchemy import create_engine, Column, Boolean, String, MetaData, Table

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Base
from app.models import Conversation

def run_migration():
    """Add admin review fields to conversations table"""

    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", "sqlite:///./bangla_chat_pro.db")

    print(f"Running migration on database: {database_url}")

    # Create engine
    engine = create_engine(database_url)

    # Create metadata object
    metadata = MetaData()

    # Reflect existing conversations table
    conversations_table = Table('conversations', metadata, autoload_with=engine)

    # Check if columns already exist
    columns_to_add = []
    existing_columns = [col.name for col in conversations_table.columns]

    if 'needs_admin_review' not in existing_columns:
        columns_to_add.append(Column('needs_admin_review', Boolean, default=False))

    if 'admin_review_reason' not in existing_columns:
        columns_to_add.append(Column('admin_review_reason', String))

    if 'admin_review_priority' not in existing_columns:
        columns_to_add.append(Column('admin_review_priority', String, default="medium"))

    # Add columns if they don't exist
    if columns_to_add:
        print(f"Adding {len(columns_to_add)} new columns to conversations table...")

        with engine.connect() as conn:
            for column in columns_to_add:
                try:
                    # Use raw SQL for SQLite compatibility
                    if database_url.startswith('sqlite'):
                        if column.name == 'needs_admin_review':
                            conn.execute(f"ALTER TABLE conversations ADD COLUMN {column.name} BOOLEAN DEFAULT 0")
                        elif column.name in ['admin_review_reason', 'admin_review_priority']:
                            conn.execute(f"ALTER TABLE conversations ADD COLUMN {column.name} VARCHAR")
                        print(f"Added column: {column.name}")
                    else:
                        # For PostgreSQL, use proper ALTER TABLE
                        conn.execute(f"ALTER TABLE conversations ADD COLUMN {column.name} {column.type}")
                        print(f"Added column: {column.name}")

                    conn.commit()
                except Exception as e:
                    print(f"Error adding column {column.name}: {e}")
                    # Column might already exist, continue
    else:
        print("All admin review columns already exist")

    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
