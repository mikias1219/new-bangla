#!/usr/bin/env python3
"""
Script to create an initial admin user for Bangla Chat Pro
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import User, Subscription, SubscriptionPlan, SubscriptionStatus, Organization, OrganizationPlan, OrganizationStatus
from app.auth.jwt import get_password_hash

def create_admin_user():
    """Create an initial admin user"""
    load_dotenv()

    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin_exists = db.query(User).filter(User.is_superuser == True).first()
        if admin_exists:
            print("Admin user already exists!")
            print(f"Email: {admin_exists.email}")
            print(f"Username: {admin_exists.username}")
            return

        # Get or create admin organization
        admin_org = db.query(Organization).filter(Organization.domain == "admin").first()
        if not admin_org:
            admin_org = Organization(
                name="Bangla Chat Pro Administration",
                domain="admin",
                description="Administrative organization for platform management",
                plan=OrganizationPlan.ENTERPRISE,
                status=OrganizationStatus.ACTIVE,
                max_users=10,
                max_ai_agents=50,
                max_monthly_chats=100000,
                is_active=True
            )
            db.add(admin_org)
            db.commit()
            db.refresh(admin_org)

        # Create admin user
        admin_email = "admin@bdchatpro.com"
        admin_username = "admin"
        admin_password = "admin123"  # Change this in production

        hashed_password = get_password_hash(admin_password)

        admin_user = User(
            organization_id=admin_org.id,
            email=admin_email,
            username=admin_username,
            hashed_password=hashed_password,
            full_name="System Administrator",
            is_active=True,
            is_superuser=True,
            is_platform_admin=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        # Create enterprise subscription for admin
        subscription = Subscription(
            user_id=admin_user.id,
            plan=SubscriptionPlan.ENTERPRISE,
            status=SubscriptionStatus.ACTIVE
        )
        db.add(subscription)
        db.commit()

        print("✅ Admin user created successfully!")
        print(f"Email: {admin_email}")
        print(f"Username: {admin_username}")
        print(f"Password: {admin_password}")
        print("\n⚠️  IMPORTANT: Change the password after first login!")

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
