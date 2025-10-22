from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..database import SessionLocal
from ..models import Conversation, Message, AIAgent, Organization
from ..auth.jwt import get_current_user, User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ConversationAnalytics(BaseModel):
    total_conversations: int
    active_conversations: int
    total_messages: int
    avg_messages_per_conversation: float
    avg_confidence_score: float
    platform_breakdown: Dict[str, int]
    daily_stats: List[Dict[str, Any]]

class MessageAnalytics(BaseModel):
    total_messages: int
    user_messages: int
    ai_messages: int
    avg_response_time: Optional[float]
    confidence_distribution: Dict[str, int]

class AgentPerformance(BaseModel):
    agent_id: int
    agent_name: str
    total_conversations: int
    total_messages: int
    avg_confidence: float
    avg_response_time: Optional[float]
    platform_usage: Dict[str, int]

@router.get("/conversations/overview", response_model=ConversationAnalytics)
async def get_conversation_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive conversation analytics"""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get conversations for the organization
        conversations = db.query(Conversation).filter(
            Conversation.organization_id == current_user.organization_id,
            Conversation.created_at >= start_date
        ).all()

        total_conversations = len(conversations)
        active_conversations = len([c for c in conversations if c.status == "active"])
        total_messages = sum(len(c.messages) for c in conversations)

        # Calculate averages
        avg_messages_per_conversation = total_messages / total_conversations if total_conversations > 0 else 0

        # Calculate confidence scores
        confidence_scores = []
        for conv in conversations:
            for msg in conv.messages:
                if msg.confidence_score is not None and msg.sender_type == "ai_agent":
                    confidence_scores.append(msg.confidence_score)

        avg_confidence_score = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        # Platform breakdown
        platform_breakdown = {}
        for conv in conversations:
            platform = conv.platform or "unknown"
            platform_breakdown[platform] = platform_breakdown.get(platform, 0) + 1

        # Daily stats for the last 30 days
        daily_stats = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            next_day = day + timedelta(days=1)

            day_conversations = [c for c in conversations if day <= c.created_at < next_day]
            day_messages = sum(len(c.messages) for c in day_conversations)

            daily_stats.append({
                "date": day.strftime("%Y-%m-%d"),
                "conversations": len(day_conversations),
                "messages": day_messages
            })

        return ConversationAnalytics(
            total_conversations=total_conversations,
            active_conversations=active_conversations,
            total_messages=total_messages,
            avg_messages_per_conversation=round(avg_messages_per_conversation, 2),
            avg_confidence_score=round(avg_confidence_score, 2),
            platform_breakdown=platform_breakdown,
            daily_stats=daily_stats
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")

@router.get("/messages/overview", response_model=MessageAnalytics)
async def get_message_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get message analytics"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get messages for the organization
        messages = db.query(Message).join(Conversation).filter(
            Conversation.organization_id == current_user.organization_id,
            Message.created_at >= start_date
        ).all()

        total_messages = len(messages)
        user_messages = len([m for m in messages if m.sender_type == "user"])
        ai_messages = len([m for m in messages if m.sender_type == "ai_agent"])

        # Confidence distribution
        confidence_distribution = {
            "high": 0,  # > 0.8
            "medium": 0,  # 0.5 - 0.8
            "low": 0  # < 0.5
        }

        for msg in messages:
            if msg.confidence_score is not None and msg.sender_type == "ai_agent":
                if msg.confidence_score > 0.8:
                    confidence_distribution["high"] += 1
                elif msg.confidence_score > 0.5:
                    confidence_distribution["medium"] += 1
                else:
                    confidence_distribution["low"] += 1

        # Average response time (placeholder - would need to track response times)
        avg_response_time = None  # This would be calculated from actual response time data

        return MessageAnalytics(
            total_messages=total_messages,
            user_messages=user_messages,
            ai_messages=ai_messages,
            avg_response_time=avg_response_time,
            confidence_distribution=confidence_distribution
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate message analytics: {str(e)}")

@router.get("/agents/performance", response_model=List[AgentPerformance])
async def get_agent_performance(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance metrics for all AI agents"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        agents = db.query(AIAgent).filter(
            AIAgent.organization_id == current_user.organization_id
        ).all()

        performance_data = []

        for agent in agents:
            # Get conversations for this agent
            conversations = db.query(Conversation).filter(
                Conversation.ai_agent_id == agent.id,
                Conversation.created_at >= start_date
            ).all()

            total_conversations = len(conversations)
            total_messages = sum(len(c.messages) for c in conversations)

            # Calculate average confidence
            confidence_scores = []
            for conv in conversations:
                for msg in conv.messages:
                    if msg.confidence_score is not None and msg.sender_type == "ai_agent":
                        confidence_scores.append(msg.confidence_score)

            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

            # Platform usage
            platform_usage = {}
            for conv in conversations:
                platform = conv.platform or "unknown"
                platform_usage[platform] = platform_usage.get(platform, 0) + 1

            performance_data.append(AgentPerformance(
                agent_id=agent.id,
                agent_name=agent.name,
                total_conversations=total_conversations,
                total_messages=total_messages,
                avg_confidence=round(avg_confidence, 2),
                avg_response_time=None,  # Placeholder
                platform_usage=platform_usage
            ))

        return performance_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate agent performance: {str(e)}")

@router.get("/conversations/recent")
async def get_recent_conversations(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent conversations with message previews"""
    try:
        conversations = db.query(Conversation).filter(
            Conversation.organization_id == current_user.organization_id
        ).order_by(Conversation.last_message_at.desc()).limit(limit).all()

        result = []
        for conv in conversations:
            # Get latest message
            latest_message = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(Message.created_at.desc()).first()

            # Get message count
            message_count = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).count()

            result.append({
                "id": conv.id,
                "platform": conv.platform,
                "user_name": conv.user_name,
                "user_phone": conv.user_phone,
                "user_email": conv.user_email,
                "status": conv.status,
                "total_messages": message_count,
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                "last_message_preview": latest_message.content[:100] + "..." if latest_message and len(latest_message.content) > 100 else (latest_message.content if latest_message else ""),
                "created_at": conv.created_at.isoformat()
            })

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent conversations: {str(e)}")

@router.get("/usage/summary")
async def get_usage_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage summary for the current month"""
    try:
        # Current month stats
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        conversations_this_month = db.query(Conversation).filter(
            Conversation.organization_id == current_user.organization_id,
            Conversation.created_at >= start_of_month
        ).count()

        messages_this_month = db.query(Message).join(Conversation).filter(
            Conversation.organization_id == current_user.organization_id,
            Message.created_at >= start_of_month
        ).count()

        # Organization limits
        org = current_user.organization

        return {
            "current_month": {
                "conversations": conversations_this_month,
                "messages": messages_this_month,
                "chats_used": org.current_monthly_chats
            },
            "limits": {
                "max_users": org.max_users,
                "max_ai_agents": org.max_ai_agents,
                "max_monthly_chats": org.max_monthly_chats
            },
            "usage_percent": {
                "chats": (org.current_monthly_chats / org.max_monthly_chats) * 100 if org.max_monthly_chats > 0 else 0
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage summary: {str(e)}")

@router.get("/conversations/{conversation_id}/details")
async def get_conversation_details(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed conversation information including full message history"""
    try:
        # Verify conversation belongs to user's organization
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get all messages with full details
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()

        # Get agent information
        agent = db.query(AIAgent).filter(AIAgent.id == conversation.ai_agent_id).first()

        return {
            "conversation": {
                "id": conversation.id,
                "platform": conversation.platform,
                "user_name": conversation.user_name,
                "user_phone": conversation.user_phone,
                "user_email": conversation.user_email,
                "status": conversation.status,
                "created_at": conversation.created_at.isoformat(),
                "last_message_at": conversation.last_message_at.isoformat() if conversation.last_message_at else None
            },
            "agent": {
                "id": agent.id if agent else None,
                "name": agent.name if agent else "Unknown",
                "description": agent.description if agent else ""
            },
            "messages": [{
                "id": msg.id,
                "content": msg.content,
                "sender_type": msg.sender_type,
                "sender_name": msg.sender_name,
                "created_at": msg.created_at.isoformat(),
                "confidence_score": msg.confidence_score,
                "message_type": msg.message_type
            } for msg in messages],
            "summary": {
                "total_messages": len(messages),
                "user_messages": len([m for m in messages if m.sender_type == "user"]),
                "ai_messages": len([m for m in messages if m.sender_type == "ai_agent"]),
                "avg_confidence": sum([m.confidence_score or 0 for m in messages if m.sender_type == "ai_agent"]) / len([m for m in messages if m.sender_type == "ai_agent"]) if messages else 0
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation details: {str(e)}")
