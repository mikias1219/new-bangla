import os
import openai
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from ..models import AIAgent, Conversation, Message, Organization
import logging
from .vector_store import VectorStore
from datetime import datetime

load_dotenv()
logger = logging.getLogger(__name__)

class AIChatService:
    """Service for handling AI conversations using trained data"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.vector_store = VectorStore()
        self.model = "gpt-4"  # Use GPT-4 for better responses

    def send_message(self, conversation_id: int, message_text: str, db: Session) -> Optional[str]:
        """Send a message to an AI agent and get a response"""
        try:
            # Get conversation and agent
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not conversation:
                return None

            agent = conversation.ai_agent
            if not agent:
                return None

            # Create user message record
            user_message = Message(
                conversation_id=conversation_id,
                content=message_text,
                sender_type="user",
                sender_name="User"
            )
            db.add(user_message)

            # Get relevant context from trained documents
            relevant_chunks = self.vector_store.search_similar_content(
                message_text,
                conversation.organization_id,
                limit=3
            )

            # Build context from relevant chunks
            context = ""
            if relevant_chunks:
                context_parts = [chunk['text'] for chunk in relevant_chunks]
                context = "\n\n".join(context_parts)

            # Generate AI response
            ai_response = self._generate_response(message_text, context, agent)

            # Create AI message record
            ai_message = Message(
                conversation_id=conversation_id,
                content=ai_response,
                sender_type="ai_agent",
                sender_name=agent.name,
                ai_response=ai_response,
                confidence_score=self._calculate_confidence(context, relevant_chunks)
            )
            db.add(ai_message)

            # Update conversation
            conversation.last_message_at = datetime.utcnow()
            conversation.total_messages += 2

            # Update agent stats
            agent.total_conversations = db.query(Conversation).filter(
                Conversation.ai_agent_id == agent.id
            ).count()
            agent.total_messages += 2

            db.commit()

            return ai_response

        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            db.rollback()
            return "I'm sorry, I encountered an error processing your message. Please try again."

    def _generate_response(self, user_message: str, context: str, agent: AIAgent) -> str:
        """Generate AI response using OpenAI with context"""
        try:
            # Build system prompt
            system_prompt = f"""You are {agent.name}, an AI assistant for {agent.organization.name}.

{agent.system_prompt}

Use the following context from the organization's training documents to provide accurate, helpful responses:
{context}

Guidelines:
- Be helpful, professional, and accurate
- Use the provided context to answer questions
- If you don't have relevant information in the context, say so politely
- Keep responses concise but informative
- Ask clarifying questions when needed"""

            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=agent.max_tokens or 1000,
                temperature=agent.temperature or 0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return "I'm sorry, I'm having trouble generating a response right now. Please try again later."

    def _calculate_confidence(self, context: str, relevant_chunks: List[Dict]) -> float:
        """Calculate confidence score based on context relevance"""
        if not relevant_chunks:
            return 0.0

        # Simple confidence calculation based on number of relevant chunks and their similarity
        avg_similarity = sum(chunk['similarity'] for chunk in relevant_chunks) / len(relevant_chunks)
        chunk_count_factor = min(len(relevant_chunks) / 3.0, 1.0)  # Max confidence from 3+ chunks

        return min(avg_similarity * chunk_count_factor, 1.0)

    def create_conversation(self, agent_id: int, platform: str = "web",
                          user_name: Optional[str] = None, user_phone: Optional[str] = None,
                          user_email: Optional[str] = None, db: Session = None) -> Optional[int]:
        """Create a new conversation"""
        try:
            agent = db.query(AIAgent).filter(AIAgent.id == agent_id).first()
            if not agent:
                return None

            conversation = Conversation(
                organization_id=agent.organization_id,
                ai_agent_id=agent_id,
                platform=platform,
                user_name=user_name,
                user_phone=user_phone,
                user_email=user_email
            )

            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            return conversation.id

        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            return None

    def get_conversation_history(self, conversation_id: int, db: Session) -> List[Dict]:
        """Get conversation history"""
        try:
            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at).all()

            return [{
                'id': msg.id,
                'content': msg.content,
                'sender_type': msg.sender_type,
                'sender_name': msg.sender_name,
                'created_at': msg.created_at.isoformat(),
                'confidence_score': msg.confidence_score
            } for msg in messages]

        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []

    def get_conversation_stats(self, agent_id: int, db: Session) -> Dict:
        """Get conversation statistics for an AI agent"""
        try:
            conversations = db.query(Conversation).filter(
                Conversation.ai_agent_id == agent_id
            ).all()

            total_conversations = len(conversations)
            total_messages = sum(len(conv.messages) for conv in conversations)
            avg_confidence = 0.0

            if total_messages > 0:
                confidence_scores = []
                for conv in conversations:
                    for msg in conv.messages:
                        if msg.confidence_score is not None:
                            confidence_scores.append(msg.confidence_score)

                if confidence_scores:
                    avg_confidence = sum(confidence_scores) / len(confidence_scores)

            return {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'average_confidence': round(avg_confidence, 2)
            }

        except Exception as e:
            logger.error(f"Error getting conversation stats: {str(e)}")
            return {
                'total_conversations': 0,
                'total_messages': 0,
                'average_confidence': 0.0
            }
