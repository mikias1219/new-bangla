from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..database import SessionLocal
from ..models import User, Subscription, SubscriptionPlan, SubscriptionStatus
from ..auth.jwt import authenticate_user, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str = None
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_username = db.query(User).filter(User.username == user.username).first()
    if db_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Get or create default organization
    from ..models import Organization, OrganizationPlan, OrganizationStatus
    default_org = db.query(Organization).filter(Organization.domain == "default").first()
    if not default_org:
        default_org = Organization(
            name="Default Organization",
            domain="default",
            description="Default organization for registered users",
            plan=OrganizationPlan.STARTER,
            status=OrganizationStatus.ACTIVE,
            max_users=1000,
            max_ai_agents=10,
            max_monthly_chats=10000,
            is_active=True
        )
        db.add(default_org)
        db.commit()
        db.refresh(default_org)

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        organization_id=default_org.id,
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create free subscription for new user
    subscription = Subscription(
        user_id=db_user.id,
        plan=SubscriptionPlan.FREE,
        status=SubscriptionStatus.TRIALING
    )
    db.add(subscription)
    db.commit()

    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        username=db_user.username,
        full_name=db_user.full_name,
        is_active=db_user.is_active
    )

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
