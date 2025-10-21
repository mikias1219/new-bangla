from sqlalchemy.orm import relationship
from .user import User
from .subscription import Subscription, SubscriptionPlan, SubscriptionStatus, SubscriptionFeature
from .payment import Payment, PaymentStatus

# Update relationships
User.subscriptions = relationship("Subscription", order_by=Subscription.id, back_populates="user")
User.payments = relationship("Payment", order_by=Payment.id, back_populates="user")
Subscription.payments = relationship("Payment", order_by=Payment.id, back_populates="subscription")
