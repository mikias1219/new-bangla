from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..database import SessionLocal
from ..models import Organization, OrganizationPlan, Subscription, Payment, PaymentStatus, User
from ..auth.jwt import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_org_owner(current_user: User = Depends(get_current_user)):
    """Require organization owner"""
    if current_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner or admin privileges required"
        )
    return current_user

class PlanDetails(BaseModel):
    id: str
    name: str
    price: float
    interval: str  # "month" or "year"
    features: List[str]
    max_users: int
    max_ai_agents: int
    max_monthly_chats: int
    description: str

class SubscriptionInfo(BaseModel):
    plan: str
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    usage: Dict[str, Any]

class PaymentHistory(BaseModel):
    id: int
    amount: float
    currency: str
    status: str
    description: str
    created_at: datetime

# Available plans configuration
PLANS = {
    "starter": PlanDetails(
        id="starter",
        name="Starter",
        price=29.99,
        interval="month",
        features=[
            "1 AI Agent",
            "1,000 chats/month",
            "Basic document training",
            "Web chat interface",
            "Email support"
        ],
        max_users=5,
        max_ai_agents=1,
        max_monthly_chats=1000,
        description="Perfect for small businesses getting started with AI chatbots"
    ),
    "professional": PlanDetails(
        id="professional",
        name="Professional",
        price=99.99,
        interval="month",
        features=[
            "3 AI Agents",
            "5,000 chats/month",
            "Advanced document training",
            "WhatsApp & Facebook integration",
            "Priority support",
            "Analytics dashboard"
        ],
        max_users=25,
        max_ai_agents=3,
        max_monthly_chats=5000,
        description="For growing businesses needing multiple AI assistants"
    ),
    "enterprise": PlanDetails(
        id="enterprise",
        name="Enterprise",
        price=299.99,
        interval="month",
        features=[
            "Unlimited AI Agents",
            "25,000 chats/month",
            "Custom AI training",
            "All integrations",
            "Dedicated support",
            "Custom branding",
            "API access"
        ],
        max_users=100,
        max_ai_agents=10,
        max_monthly_chats=25000,
        description="For large organizations with advanced AI needs"
    )
}

@router.get("/plans", response_model=List[PlanDetails])
async def get_available_plans():
    """Get all available subscription plans"""
    return list(PLANS.values())

@router.get("/plans/{plan_id}", response_model=PlanDetails)
async def get_plan_details(plan_id: str):
    """Get details for a specific plan"""
    if plan_id not in PLANS:
        raise HTTPException(status_code=404, detail="Plan not found")
    return PLANS[plan_id]

@router.get("/subscription", response_model=SubscriptionInfo)
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current subscription information"""
    org = current_user.organization

    # Calculate current usage
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # This would normally come from your subscription service
    usage = {
        "current_monthly_chats": org.current_monthly_chats,
        "max_monthly_chats": org.max_monthly_chats,
        "users_count": len(org.users),
        "max_users": org.max_users,
        "ai_agents_count": len(org.ai_agents),
        "max_ai_agents": org.max_ai_agents
    }

    return SubscriptionInfo(
        plan=org.plan.value,
        status=org.status.value,
        current_period_start=org.subscription_start,
        current_period_end=org.subscription_end,
        cancel_at_period_end=False,  # Would come from Stripe
        usage=usage
    )

@router.post("/subscription/change-plan")
async def change_plan(
    plan_id: str,
    current_user: User = Depends(require_org_owner),
    db: Session = Depends(get_db)
):
    """Change subscription plan"""
    if plan_id not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")

    if current_user.organization.plan.value == plan_id:
        raise HTTPException(status_code=400, detail="Already on this plan")

    org = current_user.organization
    new_plan = PLANS[plan_id]

    # Update organization limits
    org.plan = OrganizationPlan(plan_id)
    org.max_users = new_plan.max_users
    org.max_ai_agents = new_plan.max_ai_agents
    org.max_monthly_chats = new_plan.max_monthly_chats

    # Reset usage counters if upgrading
    if org.plan.value == "starter" and plan_id in ["professional", "enterprise"]:
        org.current_monthly_chats = 0

    db.commit()

    return {
        "message": f"Plan changed to {new_plan.name}",
        "new_plan": plan_id,
        "effective_limits": {
            "max_users": new_plan.max_users,
            "max_ai_agents": new_plan.max_ai_agents,
            "max_monthly_chats": new_plan.max_monthly_chats
        }
    }

@router.get("/payments", response_model=List[PaymentHistory])
async def get_payment_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment history for the organization"""
    # In a real implementation, this would query Stripe or your payment provider
    # For now, return mock data

    payments = [
        PaymentHistory(
            id=1,
            amount=29.99,
            currency="USD",
            status="completed",
            description="Starter Plan - Monthly",
            created_at=datetime.utcnow() - timedelta(days=30)
        ),
        PaymentHistory(
            id=2,
            amount=29.99,
            currency="USD",
            status="completed",
            description="Starter Plan - Monthly",
            created_at=datetime.utcnow() - timedelta(days=60)
        )
    ]

    return payments[:limit]

@router.post("/payments/create-intent")
async def create_payment_intent(
    plan_id: str,
    current_user: User = Depends(require_org_owner),
    db: Session = Depends(get_db)
):
    """Create a payment intent for upgrading/changing plans"""
    if plan_id not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")

    plan = PLANS[plan_id]

    # In a real implementation, this would:
    # 1. Create a Stripe PaymentIntent
    # 2. Return the client_secret for frontend payment processing

    # For now, simulate payment processing
    return {
        "client_secret": "pi_simulated_secret_" + plan_id,
        "amount": plan.price * 100,  # Convert to cents
        "currency": "usd",
        "plan_details": plan.dict()
    }

@router.post("/payments/webhook")
async def handle_payment_webhook(
    event: dict,
    db: Session = Depends(get_db)
):
    """Handle payment webhooks from Stripe"""
    # This would handle:
    # - payment_intent.succeeded
    # - customer.subscription.created
    # - customer.subscription.updated
    # - customer.subscription.deleted

    event_type = event.get("type")

    if event_type == "payment_intent.succeeded":
        # Handle successful payment
        payment_intent = event.get("data", {}).get("object", {})

        # Create payment record
        payment = Payment(
            user_id=1,  # Would need to get from metadata
            subscription_id=None,  # Would need to get from metadata
            amount=payment_intent.get("amount", 0) / 100,  # Convert from cents
            currency=payment_intent.get("currency", "usd"),
            status=PaymentStatus.COMPLETED,
            stripe_payment_id=payment_intent.get("id"),
            description="Plan upgrade payment"
        )

        db.add(payment)
        db.commit()

    elif event_type == "customer.subscription.created":
        # Handle new subscription
        subscription_data = event.get("data", {}).get("object", {})

        # Update organization subscription status
        # This would update the organization's subscription details

        pass

    return {"status": "ok"}

@router.get("/usage")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current usage statistics and limits"""
    org = current_user.organization

    # Calculate usage percentages
    chat_usage_percent = (org.current_monthly_chats / org.max_monthly_chats * 100) if org.max_monthly_chats > 0 else 0
    user_usage_percent = (len(org.users) / org.max_users * 100) if org.max_users > 0 else 0
    agent_usage_percent = (len(org.ai_agents) / org.max_ai_agents * 100) if org.max_ai_agents > 0 else 0

    return {
        "current_plan": org.plan.value,
        "status": org.status.value,
        "usage": {
            "monthly_chats": {
                "used": org.current_monthly_chats,
                "limit": org.max_monthly_chats,
                "percentage": round(chat_usage_percent, 1)
            },
            "users": {
                "used": len(org.users),
                "limit": org.max_users,
                "percentage": round(user_usage_percent, 1)
            },
            "ai_agents": {
                "used": len(org.ai_agents),
                "limit": org.max_ai_agents,
                "percentage": round(agent_usage_percent, 1)
            }
        },
        "billing_period": {
            "start": org.subscription_start.isoformat() if org.subscription_start else None,
            "end": org.subscription_end.isoformat() if org.subscription_end else None
        }
    }

@router.post("/subscription/cancel")
async def cancel_subscription(
    current_user: User = Depends(require_org_owner),
    db: Session = Depends(get_db)
):
    """Cancel subscription (downgrade to free plan)"""
    org = current_user.organization

    # In a real implementation, this would cancel the Stripe subscription
    # For now, just downgrade to starter plan

    org.plan = OrganizationPlan.STARTER
    org.max_users = PLANS["starter"].max_users
    org.max_ai_agents = PLANS["starter"].max_ai_agents
    org.max_monthly_chats = PLANS["starter"].max_monthly_chats
    org.status = OrganizationStatus.ACTIVE

    db.commit()

    return {
        "message": "Subscription cancelled. You have been moved to the Starter plan.",
        "new_plan": "starter"
    }

@router.get("/invoices")
async def get_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoice history"""
    # In a real implementation, this would fetch from Stripe
    # For now, return mock data

    return [
        {
            "id": "inv_001",
            "amount": 29.99,
            "currency": "USD",
            "status": "paid",
            "date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "description": "Starter Plan - Monthly",
            "download_url": "#"
        },
        {
            "id": "inv_002",
            "amount": 29.99,
            "currency": "USD",
            "status": "paid",
            "date": (datetime.utcnow() - timedelta(days=60)).isoformat(),
            "description": "Starter Plan - Monthly",
            "download_url": "#"
        }
    ]
