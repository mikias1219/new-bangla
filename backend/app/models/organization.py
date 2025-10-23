from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..database import Base

class OrganizationPlan(str, enum.Enum):
    STARTER = "starter"      # $29/month - 1 AI agent, 1000 chats, basic integrations
    PROFESSIONAL = "professional"  # $99/month - 3 AI agents, 5000 chats, all integrations
    ENTERPRISE = "enterprise"      # $299/month - Unlimited AI agents, unlimited chats, custom integrations

class OrganizationStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    TRIALING = "trialing"

class IVRCallStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    FAILED = "failed"

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, index=True)  # For subdomain routing
    description = Column(Text)
    logo_url = Column(String)
    website = Column(String)
    industry = Column(String)

    # Billing
    plan = Column(Enum(OrganizationPlan), nullable=False, default=OrganizationPlan.STARTER)
    status = Column(Enum(OrganizationStatus), nullable=False, default=OrganizationStatus.TRIALING)
    stripe_customer_id = Column(String, unique=True)
    trial_start = Column(DateTime(timezone=True), server_default=func.now())
    trial_end = Column(DateTime(timezone=True))
    subscription_start = Column(DateTime(timezone=True))
    subscription_end = Column(DateTime(timezone=True))

    # Limits and usage
    max_users = Column(Integer, default=5)
    max_ai_agents = Column(Integer, default=1)
    max_monthly_chats = Column(Integer, default=1000)
    current_monthly_chats = Column(Integer, default=0)

    # Settings
    timezone = Column(String, default="UTC")
    language = Column(String, default="bn")  # Default to Bangla
    is_active = Column(Boolean, default=True)

    # CRM/ERP Integration
    crm_api_url = Column(String)
    crm_api_key = Column(String)
    crm_api_secret = Column(String)
    crm_integration_enabled = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    training_documents = relationship("TrainingDocument", back_populates="organization", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="organization", cascade="all, delete-orphan")
    ai_agents = relationship("AIAgent", back_populates="organization", cascade="all, delete-orphan")
    ivr_calls = relationship("IVRCall", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name}, domain={self.domain})>"

class TrainingDocument(Base):
    __tablename__ = "training_documents"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    content_type = Column(String)  # pdf, docx, txt, csv, etc.

    # Processing status
    processing_status = Column(String, default="uploaded")  # uploaded, processing, completed, failed
    processed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)

    # Content metadata
    word_count = Column(Integer)
    page_count = Column(Integer)
    extracted_text = Column(Text)  # Full text content for search

    # Training status
    trained_at = Column(DateTime(timezone=True))
    training_status = Column(String, default="pending")  # pending, training, completed, failed

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="training_documents")

    def __repr__(self):
        return f"<TrainingDocument(id={self.id}, filename={self.filename}, status={self.processing_status})>"

class AIAgent(Base):
    __tablename__ = "ai_agents"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    avatar_url = Column(String)

    # AI Configuration
    model_name = Column(String, default="gpt-3.5-turbo")  # OpenAI model
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1000)
    system_prompt = Column(Text)

    # Integrations
    whatsapp_enabled = Column(Boolean, default=False)
    whatsapp_number = Column(String)
    facebook_enabled = Column(Boolean, default=False)
    facebook_page_id = Column(String)
    instagram_enabled = Column(Boolean, default=False)
    instagram_account_id = Column(String)

    # Training
    trained_document_ids = Column(Text)  # JSON array of document IDs
    last_trained_at = Column(DateTime(timezone=True))
    training_status = Column(String, default="not_trained")  # not_trained, training, trained, failed

    # Usage stats
    total_conversations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="ai_agents")
    conversations = relationship("Conversation", back_populates="ai_agent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AIAgent(id={self.id}, name={self.name}, organization_id={self.organization_id})>"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    ai_agent_id = Column(Integer, ForeignKey("ai_agents.id"), nullable=False)

    # External identifiers for integrations
    whatsapp_conversation_id = Column(String)
    facebook_conversation_id = Column(String)
    instagram_conversation_id = Column(String)
    web_session_id = Column(String)

    # Metadata
    platform = Column(String)  # whatsapp, facebook, instagram, web
    user_name = Column(String)
    user_phone = Column(String)
    user_email = Column(String)

    # Status
    status = Column(String, default="active")  # active, closed, archived, escalated
    last_message_at = Column(DateTime(timezone=True))

    # Human handoff tracking
    unsuccessful_responses = Column(Integer, default=0)  # Count of low-confidence responses
    escalated_to_human = Column(Boolean, default=False)
    human_agent_assigned = Column(String)  # Name/email of assigned human agent

    # Usage tracking
    total_messages = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="conversations")
    ai_agent = relationship("AIAgent", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    ivr_calls = relationship("IVRCall", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.id}, platform={self.platform}, status={self.status})>"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)

    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # text, image, file, etc.
    media_url = Column(String)

    # Sender info
    sender_type = Column(String, nullable=False)  # user, ai_agent
    sender_name = Column(String)

    # AI processing
    ai_response = Column(Text)
    confidence_score = Column(Float)
    processing_time = Column(Float)  # seconds

    # Status
    status = Column(String, default="sent")  # sent, delivered, read, failed

    # Customer satisfaction rating (1-5 scale, only for AI messages)
    satisfaction_rating = Column(Integer)  # 1-5 rating from user
    rating_feedback = Column(Text)  # Optional feedback text

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, sender_type={self.sender_type}, created_at={self.created_at})>"

class IVRCall(Base):
    __tablename__ = "ivr_calls"

    id = Column(Integer, primary_key=True, index=True)

    # Twilio call details
    twilio_call_sid = Column(String, unique=True, nullable=False)
    from_number = Column(String, nullable=False)
    to_number = Column(String, nullable=False)

    # Organization and conversation links
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    conversation_id = Column(Integer, ForeignKey("conversations.id"))

    # Call status and timing
    status = Column(Enum(IVRCallStatus), nullable=False, default=IVRCallStatus.ACTIVE)
    current_menu = Column(String, default="main")

    call_start_time = Column(DateTime(timezone=True), server_default=func.now())
    call_end_time = Column(DateTime(timezone=True))
    call_duration = Column(Float)  # seconds

    # Interaction tracking
    input_attempts = Column(Integer, default=0)
    no_input_count = Column(Integer, default=0)
    ai_interactions = Column(Integer, default=0)
    last_input_time = Column(DateTime(timezone=True))

    # AI responses and escalation
    last_ai_response = Column(Text)
    escalated_at = Column(DateTime(timezone=True))

    # Call metadata
    language_used = Column(String, default="bn")  # bn for Bangla, en for English
    user_intent = Column(String)  # order_status, product_info, support, etc.

    # Quality metrics
    call_quality_score = Column(Float)  # 1-5 scale
    user_satisfaction = Column(Integer)  # 1-5 rating if collected

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="ivr_calls")
    conversation = relationship("Conversation", back_populates="ivr_calls")

    def __repr__(self):
        return f"<IVRCall(id={self.id}, sid={self.twilio_call_sid}, status={self.status})>"

