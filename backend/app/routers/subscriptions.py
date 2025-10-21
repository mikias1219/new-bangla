from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..database import SessionLocal
from ..models import User, Subscription, SubscriptionPlan, SubscriptionStatus, SubscriptionFeature
from ..auth.jwt import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/current")
async def get_current_subscription(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not subscription:
        # Create a free subscription if none exists
        subscription = Subscription(
            user_id=current_user.id,
            plan=SubscriptionPlan.FREE,
            status=SubscriptionStatus.TRIALING
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)

    return {
        "id": subscription.id,
        "plan": subscription.plan,
        "status": subscription.status,
        "current_period_start": subscription.current_period_start,
        "current_period_end": subscription.current_period_end,
        "trial_start": subscription.trial_start,
        "trial_end": subscription.trial_end,
        "cancel_at_period_end": subscription.cancel_at_period_end
    }

@router.get("/plans")
async def get_subscription_plans():
    plans = {
        "free": {
            "name": "Free",
            "price": 0,
            "features": [
                "Basic AI chat",
                "Limited messages per day",
                "Community support"
            ]
        },
        "basic": {
            "name": "Basic",
            "price": 9.99,
            "features": [
                "Advanced AI chat",
                "Unlimited messages",
                "Priority support",
                "Voice messages"
            ]
        },
        "pro": {
            "name": "Pro",
            "price": 19.99,
            "features": [
                "Everything in Basic",
                "Custom AI models",
                "API access",
                "Advanced analytics"
            ]
        },
        "enterprise": {
            "name": "Enterprise",
            "price": 49.99,
            "features": [
                "Everything in Pro",
                "Dedicated support",
                "Custom integrations",
                "SLA guarantee"
            ]
        }
    }
    return plans

@router.post("/upgrade")
async def upgrade_subscription(
    plan: SubscriptionPlan,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.plan = plan
    subscription.status = SubscriptionStatus.ACTIVE
    db.commit()
    db.refresh(subscription)

    return {"message": f"Subscription upgraded to {plan.value}", "subscription": subscription}

@router.post("/cancel")
async def cancel_subscription(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.cancel_at_period_end = True
    db.commit()

    return {"message": "Subscription will be cancelled at the end of the billing period"}
