from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..database import Base

class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan = Column(Enum(SubscriptionPlan), nullable=False, default=SubscriptionPlan.FREE)
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.TRIALING)
    stripe_subscription_id = Column(String, unique=True)
    stripe_customer_id = Column(String)
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    trial_start = Column(DateTime(timezone=True), server_default=func.now())
    trial_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan={self.plan}, status={self.status})>"

class SubscriptionFeature(Base):
    __tablename__ = "subscription_features"

    id = Column(Integer, primary_key=True, index=True)
    plan = Column(Enum(SubscriptionPlan), nullable=False)
    feature_name = Column(String, nullable=False)
    feature_value = Column(String)  # Could be "unlimited", "100", "true", etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SubscriptionFeature(plan={self.plan}, feature={self.feature_name})>"
