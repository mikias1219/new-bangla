from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..services.ivr_service import IVRService
from ..models import Organization, IVRCall
from ..auth.jwt import get_current_user
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_ivr_service():
    """Lazy load IVR service to avoid import-time Twilio client creation"""
    return IVRService()

@router.post("/webhook/incoming-call")
async def handle_incoming_call(request: Request, db: Session = Depends(get_db)):
    """Handle incoming Twilio calls"""
    try:
        # Get form data from Twilio
        form_data = await request.form()
        call_data = dict(form_data)

        logger.info(f"Incoming call webhook: {call_data}")

        # Process the incoming call
        twiml_response = get_ivr_service().handle_incoming_call(call_data, db)

        return Response(content=twiml_response, media_type="application/xml")

    except Exception as e:
        logger.error(f"Error handling incoming call: {str(e)}")
        # Return error TwiML
        error_response = """<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="Polly.Aditi" language="bn-IN">দুঃখিত, একটি ত্রুটি হয়েছে। অনুগ্রহ করে পরে আবার চেষ্টা করুন।</Say>
            <Hangup/>
        </Response>"""
        return Response(content=error_response, media_type="application/xml")

@router.post("/webhook/process-input")
async def process_ivr_input(request: Request, db: Session = Depends(get_db)):
    """Process user input from IVR call"""
    try:
        form_data = await request.form()
        input_data = dict(form_data)

        logger.info(f"IVR input webhook: {input_data}")

        # Process the input
        twiml_response = get_ivr_service().process_ivr_input(input_data, db)

        return Response(content=twiml_response, media_type="application/xml")

    except Exception as e:
        logger.error(f"Error processing IVR input: {str(e)}")
        error_response = """<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="Polly.Aditi" language="bn-IN">দুঃখিত, ইনপুট প্রসেস করতে সমস্যা হয়েছে।</Say>
            <Hangup/>
        </Response>"""
        return Response(content=error_response, media_type="application/xml")

@router.post("/webhook/call-completed")
async def handle_call_completed(request: Request, db: Session = Depends(get_db)):
    """Handle call completion"""
    try:
        form_data = await request.form()
        call_data = dict(form_data)

        call_sid = call_data.get('CallSid')
        if call_sid:
            get_ivr_service().end_call(call_sid, db)
            logger.info(f"Call {call_sid} completed")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error handling call completion: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/main-menu")
async def get_main_menu():
    """Return main menu TwiML for redirects"""
    twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Gather input="speech dtmf" timeout="10" numDigits="1" language="bn-BD" action="/api/ivr/webhook/process-input" method="POST">
            <Say voice="Polly.Aditi" language="bn-IN">স্বাগতম বাংলা চ্যাট প্রো-তে। অনুগ্রহ করে বলুন আপনি কী সাহায্য চান?

Welcome to Bangla Chat Pro. Please say what help you need?</Say>
        </Gather>
        <Redirect>/api/ivr/main-menu</Redirect>
    </Response>"""
    return Response(content=twiml_response, media_type="application/xml")

@router.get("/calls/{organization_id}")
async def get_ivr_calls(
    organization_id: int,
    page: int = 1,
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get IVR calls for an organization"""
    try:
        # Check if user has access to this organization
        user_org_ids = [org.id for org in current_user.get("organizations", [])]
        if organization_id not in user_org_ids:
            raise HTTPException(status_code=403, detail="Access denied")

        offset = (page - 1) * limit
        calls = db.query(IVRCall).filter(
            IVRCall.organization_id == organization_id
        ).order_by(IVRCall.created_at.desc()).offset(offset).limit(limit).all()

        return {
            "calls": [{
                "id": call.id,
                "call_sid": call.twilio_call_sid,
                "from_number": call.from_number,
                "to_number": call.to_number,
                "status": call.status,
                "current_menu": call.current_menu,
                "call_duration": call.call_duration,
                "ai_interactions": call.ai_interactions,
                "language_used": call.language_used,
                "user_intent": call.user_intent,
                "call_quality_score": call.call_quality_score,
                "user_satisfaction": call.user_satisfaction,
                "created_at": call.created_at.isoformat() if call.created_at else None,
                "call_start_time": call.call_start_time.isoformat() if call.call_start_time else None,
                "call_end_time": call.call_end_time.isoformat() if call.call_end_time else None
            } for call in calls],
            "page": page,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error getting IVR calls: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/analytics/{organization_id}")
async def get_ivr_analytics(
    organization_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get IVR analytics for an organization"""
    try:
        # Check if user has access to this organization
        user_org_ids = [org.id for org in current_user.get("organizations", [])]
        if organization_id not in user_org_ids:
            raise HTTPException(status_code=403, detail="Access denied")

        analytics = get_ivr_service().get_call_analytics(organization_id, db)

        return analytics

    except Exception as e:
        logger.error(f"Error getting IVR analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/test-tts")
async def test_tts(request: Request):
    """Test TTS functionality"""
    try:
        data = await request.json()
        text = data.get("text", "এটি একটি পরীক্ষা। This is a test.")
        voice = data.get("voice", "Polly.Aditi")
        language = data.get("language", "bn-IN")

        # Generate TwiML for TTS test
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="{voice}" language="{language}">{text}</Say>
        </Response>"""

        return Response(content=twiml_response, media_type="application/xml")

    except Exception as e:
        logger.error(f"Error testing TTS: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Import Response at the top
from fastapi.responses import Response
