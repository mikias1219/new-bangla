from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import SessionLocal
from ..models import (
    User, Subscription, SubscriptionPlan, SubscriptionStatus,
    Organization, AIAgent, Conversation, Message, Payment
)
from ..auth.jwt import get_current_user, JWTBearer

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to ensure user is admin"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

class UserStats(BaseModel):
    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int

class SubscriptionStats(BaseModel):
    total_subscriptions: int
    active_subscriptions: int
    trial_subscriptions: int
    expired_subscriptions: int
    revenue_this_month: float

class SystemStats(BaseModel):
    total_conversations: int
    total_messages: int
    average_session_duration: float
    user_satisfaction_rate: float

class AIAgentStats(BaseModel):
    total_agents: int
    active_agents: int
    total_conversations: int
    average_confidence: float
    escalated_conversations: int
    platform_breakdown: dict

class AdminStats(BaseModel):
    users: UserStats
    subscriptions: SubscriptionStats
    system: SystemStats
    ai_agents: AIAgentStats

class UserManagementResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    subscription_plan: Optional[str]
    subscription_status: Optional[str]

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive admin statistics"""

    # User stats
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()

    today = datetime.utcnow().date()
    week_ago = datetime.utcnow() - timedelta(days=7)
    month_ago = datetime.utcnow() - timedelta(days=30)

    new_users_today = db.query(User).filter(
        func.date(User.created_at) == today
    ).count()

    new_users_this_week = db.query(User).filter(
        User.created_at >= week_ago
    ).count()

    new_users_this_month = db.query(User).filter(
        User.created_at >= month_ago
    ).count()

    # Subscription stats
    total_subscriptions = db.query(Subscription).count()
    active_subscriptions = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE
    ).count()
    trial_subscriptions = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.TRIALING
    ).count()
    expired_subscriptions = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.INACTIVE
    ).count()

    # Revenue calculation (simplified)
    revenue_this_month = db.query(func.sum(Payment.amount)).filter(
        Payment.created_at >= month_ago,
        Payment.status == "completed"
    ).scalar() or 0.0

    # System stats (placeholder for now)
    total_conversations = 0  # Would need conversation table
    total_messages = 0  # Would need message table
    average_session_duration = 0.0
    user_satisfaction_rate = 0.0

    # AI Agents stats
    total_agents = db.query(AIAgent).count()
    active_agents = db.query(AIAgent).filter(AIAgent.is_active == True).count()

    # AI Agents conversations (placeholder for now)
    ai_total_conversations = db.query(Conversation).count() if hasattr(db.query(Conversation), 'count') else 0
    ai_average_confidence = 0.0  # Would need message confidence scores
    ai_escalated_conversations = 0  # Would need escalation tracking

    # Platform breakdown
    platform_breakdown = {
        "web": db.query(AIAgent).filter(AIAgent.whatsapp_enabled == False, AIAgent.facebook_enabled == False).count(),
        "whatsapp": db.query(AIAgent).filter(AIAgent.whatsapp_enabled == True).count(),
        "facebook": db.query(AIAgent).filter(AIAgent.facebook_enabled == True).count(),
        "instagram": 0  # Placeholder for future Instagram integration
    }

    return AdminStats(
        users=UserStats(
            total_users=total_users,
            active_users=active_users,
            new_users_today=new_users_today,
            new_users_this_week=new_users_this_week,
            new_users_this_month=new_users_this_month
        ),
        subscriptions=SubscriptionStats(
            total_subscriptions=total_subscriptions,
            active_subscriptions=active_subscriptions,
            trial_subscriptions=trial_subscriptions,
            expired_subscriptions=expired_subscriptions,
            revenue_this_month=float(revenue_this_month)
        ),
        system=SystemStats(
            total_conversations=total_conversations,
            total_messages=total_messages,
            average_session_duration=average_session_duration,
            user_satisfaction_rate=user_satisfaction_rate
        ),
        ai_agents=AIAgentStats(
            total_agents=total_agents,
            active_agents=active_agents,
            total_conversations=ai_total_conversations,
            average_confidence=ai_average_confidence,
            escalated_conversations=ai_escalated_conversations,
            platform_breakdown=platform_breakdown
        )
    )

@router.get("/users", response_model=List[UserManagementResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users for admin management"""
    users = db.query(User).offset(skip).limit(limit).all()

    result = []
    for user in users:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id
        ).first()

        result.append(UserManagementResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            subscription_plan=subscription.plan.value if subscription else None,
            subscription_status=subscription.status.value if subscription else None
        ))

    return result

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Activate or deactivate a user account"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = is_active
    db.commit()

    return {"message": f"User {'activated' if is_active else 'deactivated'} successfully"}

@router.put("/users/{user_id}/admin")
async def toggle_admin_status(
    user_id: int,
    is_superuser: bool,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Grant or revoke admin privileges"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_superuser = is_superuser
    db.commit()

    return {"message": f"Admin privileges {'granted' if is_superuser else 'revoked'} successfully"}

@router.post("/create-admin")
async def create_admin_user(
    email: str,
    username: str,
    password: str,
    full_name: str = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new admin user"""
    # Check if user already exists
    db_user = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create admin user
    from ..auth.jwt import get_password_hash
    hashed_password = get_password_hash(password)

    db_user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        full_name=full_name,
        is_active=True,
        is_superuser=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create enterprise subscription for admin
    subscription = Subscription(
        user_id=db_user.id,
        plan=SubscriptionPlan.ENTERPRISE,
        status=SubscriptionStatus.ACTIVE
    )
    db.add(subscription)
    db.commit()

    return {"message": "Admin user created successfully", "user_id": db_user.id}

def require_platform_admin(current_user: User = Depends(require_admin)):
    """Dependency to ensure user is platform admin"""
    # For now, all admins are platform admins. In future, we could add role-based permissions
    return current_user

@router.get("/organizations")
async def get_all_organizations(
    current_user: User = Depends(require_platform_admin),
    db: Session = Depends(get_db)
):
    """Get all organizations (platform admin only)"""
    organizations = db.query(Organization).all()

    return [{
        "id": org.id,
        "name": org.name,
        "domain": org.domain,
        "plan": org.plan,
        "status": org.status,
        "max_users": org.max_users,
        "max_ai_agents": org.max_ai_agents,
        "max_monthly_chats": org.max_monthly_chats,
        "current_monthly_chats": org.current_monthly_chats,
        "created_at": org.created_at.isoformat()
    } for org in organizations]

@router.get("/ai-agents")
async def get_all_ai_agents(
    current_user: User = Depends(require_platform_admin),
    db: Session = Depends(get_db)
):
    """Get all AI agents across all organizations (platform admin only)"""
    agents = db.query(AIAgent).join(Organization).all()

    return [{
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "organization_name": agent.organization.name,
        "whatsapp_enabled": agent.whatsapp_enabled,
        "facebook_enabled": agent.facebook_enabled,
        "instagram_enabled": agent.instagram_enabled,
        "total_conversations": agent.total_conversations,
        "total_messages": agent.total_messages,
        "training_status": agent.training_status,
        "is_active": agent.is_active,
        "created_at": agent.created_at.isoformat()
    } for agent in agents]
