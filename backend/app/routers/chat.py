from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from ..database import SessionLocal
from ..models import AIAgent, Conversation, Message
from ..auth.jwt import get_current_user, User
from ..services.ai_chat import AIChatService
from ..services.background_tasks import get_background_service

router = APIRouter()
ai_chat_service = AIChatService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SendMessageRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class SendMessageResponse(BaseModel):
    response: str
    conversation_id: int
    confidence_score: Optional[float] = None

class SatisfactionRatingRequest(BaseModel):
    message_id: int
    rating: int  # 1-5 scale
    feedback: Optional[str] = None

class ConversationResponse(BaseModel):
    id: int
    platform: str
    user_name: Optional[str]
    user_phone: Optional[str]
    user_email: Optional[str]
    status: str
    total_messages: int
    last_message_at: Optional[str]
    created_at: str

class MessageResponse(BaseModel):
    id: int
    content: str
    sender_type: str
    sender_name: Optional[str]
    created_at: str
    confidence_score: Optional[float]
    satisfaction_rating: Optional[int]
    rating_feedback: Optional[str]

@router.post("/agents/{agent_id}/chat", response_model=SendMessageResponse)
async def send_message(
    agent_id: int,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to an AI agent"""
    # Verify agent belongs to user's organization
    agent = db.query(AIAgent).filter(
        AIAgent.id == agent_id,
        AIAgent.organization_id == current_user.organization_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")

    # Check usage limits
    if current_user.organization.current_monthly_chats >= current_user.organization.max_monthly_chats:
        raise HTTPException(
            status_code=429,
            detail="Monthly chat limit exceeded. Please upgrade your plan."
        )

    # Get or create conversation
    conversation_id = request.conversation_id
    if not conversation_id:
        conversation_id = ai_chat_service.create_conversation(
            agent_id=agent_id,
            platform="web",
            user_name=current_user.full_name,
            user_email=current_user.email,
            db=db
        )

        if not conversation_id:
            raise HTTPException(status_code=500, detail="Failed to create conversation")

    # Send message and get response
    response = ai_chat_service.send_message(conversation_id, request.message, db)

    if response is None:
        raise HTTPException(status_code=500, detail="Failed to process message")

    # Update usage counter
    current_user.organization.current_monthly_chats += 1
    db.commit()

    # Get confidence score from the last AI message
    confidence_score = None
    last_message = db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.sender_type == "ai_agent"
    ).order_by(Message.created_at.desc()).first()

    if last_message:
        confidence_score = last_message.confidence_score

    return SendMessageResponse(
        response=response,
        conversation_id=conversation_id,
        confidence_score=confidence_score
    )

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's conversations"""
    conversations = db.query(Conversation).filter(
        Conversation.organization_id == current_user.organization_id
    ).order_by(Conversation.last_message_at.desc()).offset(skip).limit(limit).all()

    return [{
        "id": conv.id,
        "platform": conv.platform,
        "user_name": conv.user_name,
        "user_phone": conv.user_phone,
        "user_email": conv.user_email,
        "status": conv.status,
        "total_messages": len(conv.messages),
        "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
        "created_at": conv.created_at.isoformat()
    } for conv in conversations]

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a specific conversation"""
    # Verify conversation belongs to user's organization
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.organization_id == current_user.organization_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()

    return [{
        "id": msg.id,
        "content": msg.content,
        "sender_type": msg.sender_type,
        "sender_name": msg.sender_name,
        "created_at": msg.created_at.isoformat(),
        "confidence_score": msg.confidence_score,
        "satisfaction_rating": msg.satisfaction_rating,
        "rating_feedback": msg.rating_feedback
    } for msg in messages]

@router.get("/agents/{agent_id}/stats")
async def get_agent_stats(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for an AI agent"""
    # Verify agent belongs to user's organization
    agent = db.query(AIAgent).filter(
        AIAgent.id == agent_id,
        AIAgent.organization_id == current_user.organization_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")

    stats = ai_chat_service.get_conversation_stats(agent_id, db)

    return {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "total_conversations": stats["total_conversations"],
        "total_messages": stats["total_messages"],
        "average_confidence": stats["average_confidence"],
        "training_status": agent.training_status,
        "last_trained_at": agent.last_trained_at.isoformat() if agent.last_trained_at else None
    }

@router.post("/agents/{agent_id}/train")
async def trigger_agent_training(
    agent_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger training update for an AI agent"""
    # Verify agent belongs to user's organization and user is owner/admin
    if current_user.role not in ["owner", "admin"] and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owners and admins can trigger training"
        )

    agent = db.query(AIAgent).filter(
        AIAgent.id == agent_id,
        AIAgent.organization_id == current_user.organization_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")

    # Trigger background training status update
    background_service = get_background_service()
    # Note: In a real implementation, this would trigger actual model training
    # For now, we'll just update the status based on existing documents

    return {
        "message": "Training update triggered",
        "agent_id": agent_id,
        "status": "processing"
    }

# Webhook endpoints for external integrations (WhatsApp, Facebook)
@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(
    data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle WhatsApp webhook messages"""
    from ..services.whatsapp_service import WhatsAppService

    whatsapp_service = WhatsAppService()
    success = whatsapp_service.process_webhook(data, db)

    if success:
        return {"status": "ok"}
    else:
        return {"status": "error", "message": "Failed to process webhook"}

@router.post("/webhooks/facebook")
async def facebook_webhook(
    data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle Facebook Messenger webhook messages"""
    from ..services.facebook_service import FacebookService

    facebook_service = FacebookService()
    success = facebook_service.process_webhook(data, db)

    if success:
        return {"status": "ok"}
    else:
        return {"status": "error", "message": "Failed to process webhook"}

@router.get("/webhooks/whatsapp")
async def whatsapp_webhook_verification(
    hub_mode: str,
    hub_challenge: str,
    hub_verify_token: str
):
    """Verify WhatsApp webhook"""
    from ..services.whatsapp_service import WhatsAppService

    whatsapp_service = WhatsAppService()
    challenge = whatsapp_service.verify_webhook(hub_mode, hub_challenge, hub_verify_token)

    if challenge:
        return challenge
    else:
        return {"error": "Verification failed"}

@router.get("/webhooks/facebook")
async def facebook_webhook_verification(
    hub_mode: str,
    hub_challenge: str,
    hub_verify_token: str
):
    """Verify Facebook webhook"""
    from ..services.facebook_service import FacebookService

    facebook_service = FacebookService()
    challenge = facebook_service.verify_webhook(hub_mode, hub_challenge, hub_verify_token)

    if challenge:
        return challenge
    else:
        return {"error": "Verification failed"}

@router.post("/webhooks/instagram")
async def instagram_webhook(
    data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle Instagram webhook messages"""
    from ..services.instagram_service import InstagramService

    instagram_service = InstagramService()
    success = instagram_service.process_webhook(data, db)

    if success:
        return {"status": "ok"}
    else:
        return {"status": "error", "message": "Failed to process webhook"}

@router.get("/webhooks/instagram")
async def instagram_webhook_verification(
    hub_mode: str,
    hub_challenge: str,
    hub_verify_token: str
):
    """Verify Instagram webhook"""
    from ..services.instagram_service import InstagramService

    instagram_service = InstagramService()
    challenge = instagram_service.verify_webhook(hub_mode, hub_challenge, hub_verify_token)

    if challenge:
        return challenge
    else:
        return {"error": "Verification failed"}

@router.post("/messages/rate")
async def rate_message_satisfaction(
    rating_data: SatisfactionRatingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit customer satisfaction rating for an AI message"""
    # Find the message and verify it belongs to user's organization
    message = db.query(Message).join(Conversation).filter(
        Message.id == rating_data.message_id,
        Conversation.organization_id == current_user.organization_id,
        Message.sender_type == "ai_agent"  # Only AI messages can be rated
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found or not rateable")

    # Validate rating (1-5 scale)
    if rating_data.rating < 1 or rating_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    # Update message with rating
    message.satisfaction_rating = rating_data.rating
    message.rating_feedback = rating_data.feedback

    db.commit()

    # Check if rating triggers admin review (rating below 3/5)
    if rating_data.rating < 3:
        # Log for admin review (could send notification)
        logger.warning(f"Low satisfaction rating ({rating_data.rating}/5) for message {message.id} in conversation {message.conversation_id}")

    return {"message": "Rating submitted successfully"}
