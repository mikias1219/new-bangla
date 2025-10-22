#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import User, Organization, Subscription, SubscriptionPlan, SubscriptionStatus
from app.auth.jwt import get_password_hash
from datetime import datetime, timedelta

def create_test_user():
    """Create a test user for login testing"""
    print("Creating test user...")

    db = SessionLocal()
    try:
        # Delete existing test user if exists
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            # Delete associated subscriptions first
            db.query(Subscription).filter(Subscription.user_id == existing_user.id).delete()
            db.delete(existing_user)
            db.commit()
            print("Deleted existing test user")

        # Create a test organization if it doesn't exist
        test_org = db.query(Organization).filter(Organization.domain == "test").first()
        if not test_org:
            test_org = Organization(
                name="Test Organization",
                domain="test",
                description="Test organization for development",
                plan="starter",
                status="active",
                max_users=10,
                max_ai_agents=5,
                max_monthly_chats=1000,
                is_active=True
            )
            db.add(test_org)
            db.commit()
            db.refresh(test_org)

        # Create test user with simple password
        hashed_password = get_password_hash("test")
        test_user = User(
            organization_id=test_org.id,
            email="test@example.com",
            username="testuser",
            hashed_password=hashed_password,
            full_name="Test User",
            is_active=True,
            is_superuser=False,
            is_platform_admin=False,
            role="user"
        )
        db.add(test_user)
        db.commit()  # Commit user first to get ID
        db.refresh(test_user)

        # Create subscription for test user
        subscription = Subscription(
            user_id=test_user.id,
            plan=SubscriptionPlan.FREE,
            status=SubscriptionStatus.TRIALING
        )
        db.add(subscription)

        db.commit()
        print("✅ Test user created successfully!")
        print("Username: testuser")
        print("Password: test")

    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
