import os
import stripe
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from ..database import SessionLocal
from ..models import User, Payment, PaymentStatus, Subscription, SubscriptionPlan
from ..auth.jwt import get_current_user

router = APIRouter()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_stripe_secret_key")

class PaymentIntentCreate(BaseModel):
    amount: float  # Amount in dollars
    plan: SubscriptionPlan

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create-payment-intent")
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Convert amount to cents
        amount_in_cents = int(payment_data.amount * 100)

        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency="usd",
            metadata={
                "user_id": str(current_user.id),
                "plan": payment_data.plan.value
            }
        )

        # Save payment record
        payment = Payment(
            user_id=current_user.id,
            amount=amount_in_cents,
            currency="usd",
            status=PaymentStatus.PENDING,
            stripe_payment_intent_id=intent.id,
            description=f"Subscription to {payment_data.plan.value} plan"
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return {
            "client_secret": intent.client_secret,
            "payment_id": payment.id
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request_body: dict):
    # This would handle Stripe webhooks for payment confirmations
    # For now, just acknowledge
    return {"status": "ok"}

@router.get("/history")
async def get_payment_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payments = db.query(Payment).filter(Payment.user_id == current_user.id).all()
    return [
        {
            "id": payment.id,
            "amount": payment.amount / 100,  # Convert back to dollars
            "currency": payment.currency,
            "status": payment.status,
            "description": payment.description,
            "created_at": payment.created_at
        }
        for payment in payments
    ]
