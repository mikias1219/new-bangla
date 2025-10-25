from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import SessionLocal
from ..models import (
    User, Subscription, SubscriptionPlan, SubscriptionStatus,
    Organization, AIAgent, Conversation, Message, Payment, OrganizationPlan, OrganizationStatus,
    TrainingDocument
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
    ai_total_conversations: int
    ai_average_confidence: float
    ai_escalated_conversations: int
    platform_breakdown: dict

class AIAgentStats(BaseModel):
    total_agents: int
    active_agents: int
    total_conversations: int
    average_confidence: float
    escalated_conversations: int

# Client Management Models
class ClientInfo(BaseModel):
    id: int
    name: str
    email: str
    plan: OrganizationPlan
    status: OrganizationStatus
    created_at: datetime
    ai_agents_count: int
    total_messages: int
    subscription_end: Optional[datetime] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[OrganizationPlan] = None
    status: Optional[OrganizationStatus] = None
    max_users: Optional[int] = None
    max_ai_agents: Optional[int] = None
    max_monthly_chats: Optional[int] = None

# AI Agent Management Models
class AIAgentInfo(BaseModel):
    id: int
    name: str
    organization_id: int
    organization_name: str
    status: str
    whatsapp_enabled: bool
    facebook_enabled: bool
    instagram_enabled: bool
    total_conversations: int
    created_at: datetime

class AIAgentUpdate(BaseModel):
    name: Optional[str] = None
    whatsapp_enabled: Optional[bool] = None
    facebook_enabled: Optional[bool] = None
    instagram_enabled: Optional[bool] = None
    is_active: Optional[bool] = None

# Payment Management Models
class PaymentInfo(BaseModel):
    id: int
    organization_id: int
    organization_name: str
    amount: float
    status: str
    type: str
    created_at: datetime

# AI Testing Models
class TestMessage(BaseModel):
    message: str
    ai_agent_id: Optional[int] = None

class TestResponse(BaseModel):
    response: str
    confidence: float
    ai_agent_id: int
    ai_agent_name: str

class AdminStats(BaseModel):
    users: UserStats
    subscriptions: SubscriptionStats
    system: SystemStats
    ai_agents: AIAgentStats

class CreateAIAgentRequest(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None

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

class ConversationReview(BaseModel):
    id: int
    organization_name: str
    ai_agent_name: str
    platform: str
    status: str
    needs_admin_review: bool
    admin_review_reason: str
    admin_review_priority: str
    total_messages: int
    last_message_at: str
    created_at: str
    low_ratings_count: int

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive admin statistics"""

    # Basic stats that we know work
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()

    # Simplified user growth stats
    new_users_today = 1
    new_users_this_week = total_users
    new_users_this_month = total_users

    # Subscription stats (simplified)
    total_subscriptions = db.query(Subscription).count() if Subscription else 0
    active_subscriptions = 0
    trial_subscriptions = 0
    expired_subscriptions = 0
    revenue_this_month = 0.0

    # System stats (simplified)
    total_conversations = 0
    total_messages = 0
    average_session_duration = 5.2  # Mock value
    user_satisfaction_rate = 85.0  # Mock value

    # AI Agents stats (simplified)
    total_agents = db.query(AIAgent).count() if AIAgent else 0
    active_agents = db.query(AIAgent).filter(AIAgent.is_active == True).count() if AIAgent else 0
    ai_total_conversations = total_conversations
    ai_average_confidence = 0.82
    ai_escalated_conversations = 0

    # Platform breakdown (mock)
    platform_breakdown = {
        "web": 25,
        "whatsapp": 25,
        "facebook": 25,
        "ivr": 25
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
            user_satisfaction_rate=user_satisfaction_rate,
            ai_total_conversations=ai_total_conversations,
            ai_average_confidence=ai_average_confidence,
            ai_escalated_conversations=ai_escalated_conversations,
            platform_breakdown=platform_breakdown
        ),
        ai_agents=AIAgentStats(
            total_agents=total_agents,
            active_agents=active_agents,
            total_conversations=ai_total_conversations,
            average_confidence=ai_average_confidence,
            escalated_conversations=ai_escalated_conversations
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

@router.post("/organizations/{org_id}/ai-agents")
async def create_ai_agent_for_organization(
    org_id: int,
    agent_data: CreateAIAgentRequest,
    current_user: User = Depends(require_platform_admin),
    db: Session = Depends(get_db)
):
    """Create a new AI agent for a specific organization (admin only)"""
    # Verify organization exists
    organization = db.query(Organization).filter(Organization.id == org_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check agent limits for the organization
    agent_count = db.query(AIAgent).filter(AIAgent.organization_id == org_id).count()
    if agent_count >= organization.max_ai_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Organization has reached maximum AI agents limit ({organization.max_ai_agents})"
        )

    # Create system prompt tailored to the organization
    system_prompt = agent_data.system_prompt
    if not system_prompt:
        system_prompt = f"""You are {agent_data.name}, an AI assistant for {organization.name}.
        You help customers with their inquiries about {organization.name}'s products and services.
        Be helpful, professional, and knowledgeable about {organization.name}.
        Always respond in a friendly and customer-service oriented manner.
        If you don't know something specific, be honest and offer to connect them with a human representative."""

    agent = AIAgent(
        organization_id=org_id,
        name=agent_data.name,
        description=agent_data.description,
        system_prompt=system_prompt,
        training_status="created"
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "organization_name": organization.name,
        "status": "created",
        "message": f"AI agent created successfully for {organization.name}"
    }

@router.put("/ai-agents/{agent_id}/status")
async def update_ai_agent_status(
    agent_id: int,
    is_active: bool,
    current_user: User = Depends(require_platform_admin),
    db: Session = Depends(get_db)
):
    """Activate or deactivate an AI agent"""
    agent = db.query(AIAgent).filter(AIAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")

    agent.is_active = is_active
    agent.training_status = "trained" if is_active else "inactive"
    db.commit()

    return {"message": f"AI agent {'activated' if is_active else 'deactivated'} successfully"}

@router.post("/test-openai")
async def test_openai_directly(
    message: str,
    model: str = "gpt-4",
    system_prompt: str = "You are a helpful AI assistant.",
    current_user: User = Depends(require_platform_admin),
    db: Session = Depends(get_db)
):
    """Test OpenAI integration directly without specific agent (admin only)"""
    try:
        from ..services.ai_chat import AIChatService
        from ..models import Organization, AIAgent
        ai_service = AIChatService()

        # Create temporary organization and agent for testing
        temp_org = Organization(
            name="Admin Test Org",
            domain="admin-test",
            description="Temporary organization for admin testing",
            plan="starter",
            status="active",
            max_users=1,
            max_ai_agents=1,
            max_monthly_chats=100,
            current_monthly_chats=0
        )
        db.add(temp_org)
        db.commit()

        temp_agent = AIAgent(
            organization_id=temp_org.id,
            name="Admin Test Agent",
            description="Temporary agent for admin testing",
            system_prompt=system_prompt,
            training_status="trained",
            is_active=True
        )
        db.add(temp_agent)
        db.commit()

        # Create conversation using the AI chat service
        conversation_id = ai_service.create_conversation(
            agent_id=temp_agent.id,
            platform="admin_test",
            user_name="Admin Tester",
            user_email=current_user.email,
            db=db
        )

        if not conversation_id:
            raise HTTPException(status_code=500, detail="Failed to create test conversation")

        # Send the message
        response = ai_service.send_message(conversation_id, message, db)

        # Clean up temporary data
        db.delete(temp_agent)
        db.delete(temp_org)
        db.commit()

        if response:
            return {"response": response, "model": model, "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Failed to get response from OpenAI")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI test failed: {str(e)}")

@router.get("/conversations/needs-review", response_model=List[ConversationReview])
async def get_conversations_needing_review(
    priority: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get conversations that need admin review due to low satisfaction ratings"""

    # Build query
    query = db.query(Conversation).join(Organization).join(AIAgent).filter(
        Conversation.needs_admin_review == True
    )

    # Filter by priority if specified
    if priority:
        query = query.filter(Conversation.admin_review_priority == priority)

    # Order by priority (high first) and creation date
    priority_order = {
        'high': 1,
        'medium': 2,
        'low': 3
    }

    conversations = query.order_by(
        Conversation.created_at.desc()  # Simple ordering for now
    ).limit(limit).all()

    result = []
    for conv in conversations:
        # Count low ratings (1 or 2 stars) in this conversation
        low_ratings_count = db.query(func.count(Message.id)).filter(
            Message.conversation_id == conv.id,
            Message.satisfaction_rating <= 2
        ).scalar()

        result.append({
            "id": conv.id,
            "organization_name": conv.organization.name,
            "ai_agent_name": conv.ai_agent.name,
            "platform": conv.platform or "unknown",
            "status": conv.status,
            "needs_admin_review": conv.needs_admin_review,
            "admin_review_reason": conv.admin_review_reason or "",
            "admin_review_priority": conv.admin_review_priority,
            "total_messages": conv.total_messages,
            "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else conv.created_at.isoformat(),
            "created_at": conv.created_at.isoformat(),
            "low_ratings_count": low_ratings_count
        })

    return result

@router.put("/conversations/{conversation_id}/review-status")
async def update_conversation_review_status(
    conversation_id: int,
    needs_review: bool = False,
    review_reason: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update admin review status for a conversation"""

    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation.needs_admin_review = needs_review
    if review_reason is not None:
        conversation.admin_review_reason = review_reason

    db.commit()

    return {"message": "Conversation review status updated successfully"}

# ===============================
# CLIENT MANAGEMENT ENDPOINTS
# ===============================

@router.get("/clients", response_model=List[ClientInfo])
async def get_all_clients(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all clients with their details"""
    organizations = db.query(Organization).all()

    clients = []
    for org in organizations:
        # Count AI agents
        ai_agents_count = db.query(func.count(AIAgent.id)).filter(
            AIAgent.organization_id == org.id
        ).scalar() or 0

        # Count total messages (simplified for now)
        total_messages = 0  # Simplified to avoid query issues

        clients.append({
            "id": org.id,
            "name": org.name,
            "email": "",  # Organizations don't have email directly, would need to get from users
            "plan": org.plan,
            "status": org.status,
            "created_at": org.created_at,
            "ai_agents_count": ai_agents_count,
            "total_messages": total_messages,
            "subscription_end": org.subscription_end
        })

    return clients

@router.put("/clients/{client_id}")
async def update_client(
    client_id: int,
    client_update: ClientUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update client details and handle subscription changes"""
    organization = db.query(Organization).filter(Organization.id == client_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Client not found")

    # Update fields
    for field, value in client_update.dict(exclude_unset=True).items():
        if field == "status" and value != "active":
            # Deactivate all AI agents for this client
            db.query(AIAgent).filter(AIAgent.organization_id == client_id).update({
                "is_active": False
            })
        setattr(organization, field, value)

    db.commit()

    return {"message": "Client updated successfully"}

@router.delete("/clients/{client_id}")
async def delete_client(
    client_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a client and all their data"""
    organization = db.query(Organization).filter(Organization.id == client_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Client not found")

    # This will cascade delete all related data (users, agents, conversations, etc.)
    db.delete(organization)
    db.commit()

    return {"message": "Client deleted successfully"}

# ===============================
# AI AGENT MANAGEMENT ENDPOINTS
# ===============================

@router.get("/ai-agents", response_model=List[AIAgentInfo])
async def get_all_ai_agents(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all AI agents across all clients"""
    agents = db.query(AIAgent).join(Organization).all()

    return [{
        "id": agent.id,
        "name": agent.name,
        "organization_id": agent.organization_id,
        "organization_name": agent.organization.name,
        "status": "active" if agent.is_active else "inactive",
        "whatsapp_enabled": agent.whatsapp_enabled,
        "facebook_enabled": agent.facebook_enabled,
        "instagram_enabled": agent.instagram_enabled,
        "total_conversations": agent.total_conversations,
        "created_at": agent.created_at
    } for agent in agents]

@router.put("/ai-agents/{agent_id}")
async def update_ai_agent(
    agent_id: int,
    agent_update: AIAgentUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update AI agent settings"""
    agent = db.query(AIAgent).filter(AIAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="AI Agent not found")

    # Update fields
    for field, value in agent_update.dict(exclude_unset=True).items():
        setattr(agent, field, value)

    db.commit()

    return {"message": "AI Agent updated successfully"}

@router.delete("/ai-agents/{agent_id}")
async def delete_ai_agent(
    agent_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete an AI agent"""
    agent = db.query(AIAgent).filter(AIAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="AI Agent not found")

    db.delete(agent)
    db.commit()

    return {"message": "AI Agent deleted successfully"}

# ===============================
# PAYMENT MANAGEMENT ENDPOINTS
# ===============================

@router.get("/payments", response_model=List[PaymentInfo])
async def get_all_payments(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all payments across all clients"""
    payments = db.query(Payment).join(User).join(Organization).all()

    return [{
        "id": payment.id,
        "organization_id": payment.user.organization_id,
        "organization_name": payment.user.organization.name,
        "amount": payment.amount,
        "status": payment.status,
        "type": payment.type,
        "created_at": payment.created_at
    } for payment in payments]

@router.post("/payments/{payment_id}/retry")
async def retry_payment(
    payment_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Retry a failed payment"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status != "failed":
        raise HTTPException(status_code=400, detail="Payment is not in failed state")

    # Here you would integrate with your payment processor (Stripe, etc.)
    # For now, we'll just mark it as paid
    payment.status = "paid"
    db.commit()

    return {"message": "Payment retry initiated"}

# ===============================
# AI TESTING ENDPOINTS
# ===============================

@router.post("/test-ai", response_model=TestResponse)
async def test_ai_agent(
    test_request: TestMessage,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Test an AI agent with a message"""
    agent = None
    if test_request.ai_agent_id:
        agent = db.query(AIAgent).filter(AIAgent.id == test_request.ai_agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="AI Agent not found")
    else:
        # Use first active agent as default
        agent = db.query(AIAgent).filter(AIAgent.is_active == True).first()
        if not agent:
            raise HTTPException(status_code=404, detail="No active AI agents found")

    # Here you would integrate with your AI service (OpenAI, etc.)
    # For now, return a mock response
    mock_response = f"This is a test response from {agent.name} for the message: '{test_request.message}'"

    return {
        "response": mock_response,
        "confidence": 0.85,
        "ai_agent_id": agent.id,
        "ai_agent_name": agent.name
    }

@router.post("/test-ivr")
async def test_ivr_call(
    test_request: TestMessage,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Test IVR functionality"""
    agent = None
    if test_request.ai_agent_id:
        agent = db.query(AIAgent).filter(AIAgent.id == test_request.ai_agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="AI Agent not found")
    else:
        # Use first active agent as default
        agent = db.query(AIAgent).filter(AIAgent.is_active == True).first()
        if not agent:
            raise HTTPException(status_code=404, detail="No active AI agents found")

    # Here you would integrate with your IVR service (Twilio, etc.)
    # For now, return a mock response
    mock_ivr_response = f"IVR Test: Welcome! You said '{test_request.message}'. How can I help you today?"

    return {
        "response": mock_ivr_response,
        "agent_name": agent.name,
        "ivr_status": "completed"
    }
