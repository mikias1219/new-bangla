from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn

from .database import SessionLocal, engine, Base
from .models import user, subscription, payment
from .routers import auth, users, subscriptions, payments, ai_agent, admin, organizations, chat, analytics, billing
from .auth.jwt import JWTBearer

# Create database tables (only if they don't exist)
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Database tables creation skipped: {e}")

app = FastAPI(
    title="Bangla Chat Pro API",
    description="AI-powered chat platform with subscription management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
        "https://bdchatpro.com",
        "https://www.bdchatpro.com"
    ],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(ai_agent.router, prefix="/ai", tags=["AI Agent"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(billing.router, prefix="/billing", tags=["Billing"])

@app.get("/")
async def root():
    return {"message": "Bangla Chat Pro API", "status": "running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
