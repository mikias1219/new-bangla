#!/usr/bin/env python3
"""
Migration script to add IVR calls table to the database
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from sqlalchemy import create_engine, text
from app.database import DATABASE_URL

def add_ivr_table():
    """Add IVR calls table to the database"""
    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as conn:
            # Check if table already exists
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='ivr_calls';"))
            if result.fetchone():
                print("IVR calls table already exists!")
                return

            # Create IVR calls table
            create_table_sql = """
            CREATE TABLE ivr_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                twilio_call_sid VARCHAR UNIQUE NOT NULL,
                from_number VARCHAR NOT NULL,
                to_number VARCHAR NOT NULL,
                organization_id INTEGER,
                conversation_id INTEGER,
                status VARCHAR DEFAULT 'active',
                current_menu VARCHAR DEFAULT 'main',
                call_start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                call_end_time DATETIME,
                call_duration REAL,
                input_attempts INTEGER DEFAULT 0,
                no_input_count INTEGER DEFAULT 0,
                ai_interactions INTEGER DEFAULT 0,
                last_input_time DATETIME,
                last_ai_response TEXT,
                escalated_at DATETIME,
                language_used VARCHAR DEFAULT 'bn',
                user_intent VARCHAR,
                call_quality_score REAL,
                user_satisfaction INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations (id),
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            );
            """

            conn.execute(text(create_table_sql))
            conn.commit()

            print("✅ IVR calls table created successfully!")

            # Create indexes for better performance
            indexes_sql = [
                "CREATE INDEX idx_ivr_calls_twilio_sid ON ivr_calls(twilio_call_sid);",
                "CREATE INDEX idx_ivr_calls_organization ON ivr_calls(organization_id);",
                "CREATE INDEX idx_ivr_calls_status ON ivr_calls(status);",
                "CREATE INDEX idx_ivr_calls_created_at ON ivr_calls(created_at);"
            ]

            for index_sql in indexes_sql:
                try:
                    conn.execute(text(index_sql))
                    print(f"✅ Created index: {index_sql.split('ON')[0].strip()}")
                except Exception as e:
                    print(f"⚠️  Index creation failed (might already exist): {e}")

            conn.commit()
            print("✅ All IVR table indexes created successfully!")

    except Exception as e:
        print(f"❌ Error creating IVR table: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Adding IVR calls table to database...")
    add_ivr_table()
    print("✅ Migration completed!")
