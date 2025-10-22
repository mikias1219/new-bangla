#!/usr/bin/env python3
"""
Migration script to add multi-tenant architecture to Bangla Chat Pro
This script will:
1. Create new organization-related tables
2. Migrate existing users to a default organization
3. Set up platform admin user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import (
    Organization, OrganizationPlan, OrganizationStatus,
    TrainingDocument, AIAgent, Conversation, Message
)
from app.auth.jwt import get_password_hash
from datetime import datetime, timedelta
import shutil

def migrate_database():
    """Migrate database to multi-tenant architecture"""
    print("🚀 Starting multi-tenant migration...")

    # Create new tables
    print("📦 Creating new tables...")
    try:
        Organization.__table__.create(engine, checkfirst=True)
        TrainingDocument.__table__.create(engine, checkfirst=True)
        AIAgent.__table__.create(engine, checkfirst=True)
        Conversation.__table__.create(engine, checkfirst=True)
        Message.__table__.create(engine, checkfirst=True)
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

    # Use raw SQL to avoid model relationship issues
    from sqlalchemy import text

    db = SessionLocal()
    try:
        # Check if migration already done
        result = db.execute(text("SELECT COUNT(*) FROM organizations")).scalar()
        if result > 0:
            print("ℹ️  Migration already completed")
            return True

        # Create platform organization (for platform admins)
        print("🏢 Creating platform organization...")
        db.execute(text("""
            INSERT INTO organizations (name, domain, description, plan, status, max_users, max_ai_agents, max_monthly_chats, is_active)
            VALUES (:name, :domain, :description, :plan, :status, :max_users, :max_ai_agents, :max_monthly_chats, :is_active)
        """), {
            'name': 'Bangla Chat Pro Platform',
            'domain': 'platform',
            'description': 'Platform administration organization',
            'plan': 'enterprise',
            'status': 'active',
            'max_users': 10,
            'max_ai_agents': 10,
            'max_monthly_chats': 100000,
            'is_active': True
        })

        platform_org_id = db.execute(text("SELECT id FROM organizations WHERE domain = 'platform'")).scalar()

        # Create default organization for existing users
        print("🏢 Creating default organization...")
        db.execute(text("""
            INSERT INTO organizations (name, domain, description, plan, status, max_users, max_ai_agents, max_monthly_chats, is_active)
            VALUES (:name, :domain, :description, :plan, :status, :max_users, :max_ai_agents, :max_monthly_chats, :is_active)
        """), {
            'name': 'Default Organization',
            'domain': 'default',
            'description': 'Default organization for existing users',
            'plan': 'starter',
            'status': 'active',
            'max_users': 100,
            'max_ai_agents': 5,
            'max_monthly_chats': 10000,
            'is_active': True
        })

        default_org_id = db.execute(text("SELECT id FROM organizations WHERE domain = 'default'")).scalar()

        # Add organization_id column to users table
        print("👥 Migrating existing users...")
        db.execute(text("ALTER TABLE users ADD COLUMN organization_id INTEGER"))
        db.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user'"))
        db.execute(text("ALTER TABLE users ADD COLUMN is_platform_admin BOOLEAN DEFAULT FALSE"))

        # Update existing users
        user_count = db.execute(text(f"UPDATE users SET organization_id = {default_org_id}")).rowcount
        db.execute(text(f"UPDATE users SET role = 'owner' WHERE is_superuser = TRUE"))
        db.execute(text(f"UPDATE users SET is_platform_admin = is_superuser"))

        # Create platform admin user if not exists
        existing_admin = db.execute(text("SELECT id FROM users WHERE username = 'admin'")).scalar()
        if not existing_admin:
            print("👑 Creating platform admin user...")
            db.execute(text("""
                INSERT INTO users (organization_id, email, username, hashed_password, full_name, is_active, is_superuser, is_platform_admin, role)
                VALUES (:org_id, :email, :username, :password, :full_name, :is_active, :is_superuser, :is_platform_admin, :role)
            """), {
                'org_id': platform_org_id,
                'email': 'admin@bdchatpro.com',
                'username': 'admin',
                'password': get_password_hash('admin123'),
                'full_name': 'Platform Administrator',
                'is_active': True,
                'is_superuser': True,
                'is_platform_admin': True,
                'role': 'owner'
            })

        # Create uploads directory
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            print("📁 Created uploads directory")

        db.commit()

        print("✅ Migration completed successfully!")
        print("📋 Summary:")
        print("   - Platform organization: Bangla Chat Pro Platform")
        print("   - Default organization: Default Organization")
        print(f"   - Migrated users: {user_count}")
        print("   - Platform admin: admin")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
