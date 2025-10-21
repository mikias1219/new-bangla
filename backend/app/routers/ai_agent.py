import os
from openai import OpenAI
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from ..database import SessionLocal
from ..models import User, Subscription, SubscriptionPlan, SubscriptionStatus
from ..auth.jwt import get_current_user

router = APIRouter()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
client = OpenAI(api_key=api_key)

class ChatMessage(BaseModel):
    message: str
    conversation_id: str = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_subscription_limits(user: User, db: Session):
    """Check if user has exceeded their subscription limits"""
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()

    if not subscription:
        raise HTTPException(status_code=403, detail="No active subscription found")

    # Check if subscription is active or in trial
    if subscription.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
        raise HTTPException(status_code=403, detail="Subscription is not active")

    # Check trial expiration
    if subscription.status == SubscriptionStatus.TRIALING and subscription.trial_end:
        if datetime.utcnow() > subscription.trial_end:
            subscription.status = SubscriptionStatus.INACTIVE
            db.commit()
            raise HTTPException(status_code=403, detail="Trial period has expired")

    return subscription

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_data: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check subscription limits
    subscription = check_subscription_limits(current_user, db)

    try:
        # Create system prompt based on subscription plan
        system_prompt = get_system_prompt_for_plan(subscription.plan)

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chat_data.message}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content

        # Generate conversation ID if not provided
        conversation_id = chat_data.conversation_id or f"conv_{current_user.id}_{datetime.utcnow().timestamp()}"

        return ChatResponse(
            response=ai_response,
            conversation_id=conversation_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

def get_system_prompt_for_plan(plan: SubscriptionPlan) -> str:
    """Get system prompt based on subscription plan"""
    base_prompt = "You are a helpful AI assistant for Bangla Chat Pro."

    if plan == SubscriptionPlan.FREE:
        return base_prompt + " You provide basic assistance and answer general questions."
    elif plan == SubscriptionPlan.BASIC:
        return base_prompt + " You provide advanced assistance, can help with coding, writing, and general tasks."
    elif plan == SubscriptionPlan.PRO:
        return base_prompt + " You are an expert AI assistant with advanced capabilities, including creative writing, technical analysis, and complex problem-solving."
    elif plan == SubscriptionPlan.ENTERPRISE:
        return base_prompt + " You are a premium AI assistant with the highest level of expertise, providing comprehensive solutions, strategic advice, and specialized knowledge."
    else:
        return base_prompt

@router.get("/usage")
async def get_usage_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's AI usage statistics"""
    subscription = check_subscription_limits(current_user, db)

    # This would typically track actual usage from a separate table
    # For now, return basic subscription info
    return {
        "plan": subscription.plan,
        "status": subscription.status,
        "trial_end": subscription.trial_end,
        "messages_remaining": "unlimited" if subscription.plan != SubscriptionPlan.FREE else "limited"
    }
