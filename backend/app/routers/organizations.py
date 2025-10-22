from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from datetime import datetime

from ..database import SessionLocal
from ..models import (
    Organization, OrganizationPlan, OrganizationStatus,
    TrainingDocument, AIAgent, User
)
from ..auth.jwt import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_org_owner(current_user: User = Depends(get_current_user)):
    """Require organization owner or platform admin"""
    if not (current_user.role == "owner" or current_user.is_platform_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner or admin privileges required"
        )
    return current_user

class OrganizationCreate(BaseModel):
    name: str
    domain: str
    description: Optional[str] = None
    industry: Optional[str] = None
    plan: OrganizationPlan = OrganizationPlan.STARTER

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    plan: Optional[OrganizationPlan] = None

class OrganizationResponse(BaseModel):
    id: int
    name: str
    domain: str
    description: Optional[str]
    industry: Optional[str]
    plan: OrganizationPlan
    status: OrganizationStatus
    max_users: int
    max_ai_agents: int
    max_monthly_chats: int
    current_monthly_chats: int
    created_at: datetime

@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new organization (only platform admins can do this)"""
    if not current_user.is_platform_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform administrators can create organizations"
        )

    # Check if domain is unique
    existing_org = db.query(Organization).filter(Organization.domain == org_data.domain).first()
    if existing_org:
        raise HTTPException(status_code=400, detail="Domain already taken")

    # Create organization
    org = Organization(
        name=org_data.name,
        domain=org_data.domain,
        description=org_data.description,
        industry=org_data.industry,
        plan=org_data.plan
    )

    # Set limits based on plan
    if org.plan == OrganizationPlan.STARTER:
        org.max_users = 5
        org.max_ai_agents = 1
        org.max_monthly_chats = 1000
    elif org.plan == OrganizationPlan.PROFESSIONAL:
        org.max_users = 25
        org.max_ai_agents = 3
        org.max_monthly_chats = 5000
    elif org.plan == OrganizationPlan.ENTERPRISE:
        org.max_users = 100
        org.max_ai_agents = 10
        org.max_monthly_chats = 25000

    db.add(org)
    db.commit()
    db.refresh(org)

    # Create owner user (first user of the organization)
    owner_user = User(
        organization_id=org.id,
        email=current_user.email,
        username=current_user.username,
        hashed_password=current_user.hashed_password,
        full_name=current_user.full_name,
        role="owner",
        is_superuser=True
    )

    db.add(owner_user)
    db.commit()

    return org

@router.get("/my", response_model=OrganizationResponse)
async def get_my_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's organization"""
    # Explicitly load the organization to avoid DetachedInstanceError
    organization = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

@router.put("/my", response_model=OrganizationResponse)
async def update_my_organization(
    org_data: OrganizationUpdate,
    current_user: User = Depends(require_org_owner),
    db: Session = Depends(get_db)
):
    """Update organization (owner only)"""
    # Explicitly load the organization to avoid DetachedInstanceError
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if org_data.name:
        org.name = org_data.name
    if org_data.description is not None:
        org.description = org_data.description
    if org_data.industry is not None:
        org.industry = org_data.industry
    if org_data.plan:
        org.plan = org_data.plan

    db.commit()
    db.refresh(org)
    return org

@router.post("/documents/upload")
async def upload_training_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a training document for the organization"""
    # Validate file type
    allowed_types = [
        'application/pdf', 'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain', 'text/csv', 'application/rtf'
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Create uploads directory if it doesn't exist
    org_upload_dir = f"uploads/organizations/{current_user.organization_id}"
    os.makedirs(org_upload_dir, exist_ok=True)

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{datetime.utcnow().timestamp()}_{file.filename}"

    file_path = os.path.join(org_upload_dir, unique_filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create training document record
    doc = TrainingDocument(
        organization_id=current_user.organization_id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        mime_type=file.content_type,
        content_type=file_extension[1:]  # Remove the dot
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "id": doc.id,
        "filename": doc.original_filename,
        "status": doc.processing_status,
        "message": "Document uploaded successfully. Processing will begin shortly."
    }

@router.get("/documents")
async def get_training_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all training documents for the organization"""
    docs = db.query(TrainingDocument).filter(
        TrainingDocument.organization_id == current_user.organization_id
    ).all()

    return [{
        "id": doc.id,
        "filename": doc.original_filename,
        "status": doc.processing_status,
        "word_count": doc.word_count,
        "uploaded_at": doc.created_at,
        "trained_at": doc.trained_at
    } for doc in docs]

@router.post("/ai-agents")
async def create_ai_agent(
    name: str,
    description: Optional[str] = None,
    current_user: User = Depends(require_org_owner),
    db: Session = Depends(get_db)
):
    """Create a new AI agent for the organization"""
    # Check limits
    agent_count = db.query(AIAgent).filter(
        AIAgent.organization_id == current_user.organization_id
    ).count()

    if agent_count >= current_user.organization.max_ai_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum AI agents limit reached ({current_user.organization.max_ai_agents})"
        )

    agent = AIAgent(
        organization_id=current_user.organization_id,
        name=name,
        description=description,
        system_prompt=f"You are {name}, an AI assistant for {current_user.organization.name}. Be helpful and professional."
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "status": "created"
    }

@router.get("/ai-agents")
async def get_ai_agents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all AI agents for the organization"""
    agents = db.query(AIAgent).filter(
        AIAgent.organization_id == current_user.organization_id
    ).all()

    return [{
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "whatsapp_enabled": agent.whatsapp_enabled,
        "facebook_enabled": agent.facebook_enabled,
        "instagram_enabled": agent.instagram_enabled,
        "total_conversations": agent.total_conversations,
        "training_status": agent.training_status
    } for agent in agents]

@router.put("/ai-agents/{agent_id}/integrations/whatsapp")
async def configure_whatsapp_integration(
    agent_id: int,
    phone_number: str,
    current_user: User = Depends(require_org_owner),
    db: Session = Depends(get_db)
):
    """Configure WhatsApp integration for an AI agent"""
    agent = db.query(AIAgent).filter(
        AIAgent.id == agent_id,
        AIAgent.organization_id == current_user.organization_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")

    agent.whatsapp_enabled = True
    agent.whatsapp_number = phone_number

    db.commit()

    return {"message": "WhatsApp integration configured successfully"}

@router.put("/ai-agents/{agent_id}/integrations/facebook")
async def configure_facebook_integration(
    agent_id: int,
    page_id: str,
    current_user: User = Depends(require_org_owner),
    db: Session = Depends(get_db)
):
    """Configure Facebook Messenger integration for an AI agent"""
    agent = db.query(AIAgent).filter(
        AIAgent.id == agent_id,
        AIAgent.organization_id == current_user.organization_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")

    agent.facebook_enabled = True
    agent.facebook_page_id = page_id

    db.commit()

    return {"message": "Facebook integration configured successfully"}

@router.put("/ai-agents/{agent_id}/integrations/instagram")
async def configure_instagram_integration(
    agent_id: int,
    account_id: str,
    current_user: User = Depends(require_org_owner),
    db: Session = Depends(get_db)
):
    """Configure Instagram Business Messaging integration for an AI agent"""
    agent = db.query(AIAgent).filter(
        AIAgent.id == agent_id,
        AIAgent.organization_id == current_user.organization_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")

    agent.instagram_enabled = True
    agent.instagram_account_id = account_id

    db.commit()

    return {"message": "Instagram integration configured successfully"}

@router.put("/integrations/crm")
async def configure_crm_integration(
    api_url: str,
    api_key: str,
    api_secret: Optional[str] = None,
    current_user: User = Depends(require_org_owner),
    db: Session = Depends(get_db)
):
    """Configure CRM/ERP API integration for the organization"""
    org = current_user.organization

    org.crm_api_url = api_url
    org.crm_api_key = api_key
    org.crm_api_secret = api_secret
    org.crm_integration_enabled = True

    db.commit()
    db.refresh(org)

    # Test the connection
    from ..services.api_integration_service import APIIntegrationService
    crm_service = APIIntegrationService(org)
    connection_test = crm_service.test_connection()

    return {
        "message": "CRM integration configured successfully",
        "connection_test": "passed" if connection_test else "failed",
        "api_url": api_url
    }

