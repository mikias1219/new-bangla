import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from twilio.twiml.voice_response import VoiceResponse, Gather, Say, Dial, Play
from twilio.rest import Client
from sqlalchemy.orm import Session
from ..models import Conversation, IVRCall, Organization
from .ai_chat import AIChatService
from .background_tasks import BackgroundTaskManager
import asyncio

logger = logging.getLogger(__name__)

class IVRService:
    """Comprehensive IVR service for handling phone calls with AI assistance"""

    def __init__(self):
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.ai_service = AIChatService()
        self.task_manager = BackgroundTaskManager()

        # IVR Menu Configuration
        self.ivr_menus = {
            "main": {
                "message": "স্বাগতম বাংলা চ্যাট প্রো-তে। অনুগ্রহ করে বলুন আপনি কী সাহায্য চান?\n\nWelcome to Bangla Chat Pro. Please say what help you need?",
                "options": {
                    "1": {"label": "অর্ডার স্ট্যাটাস / Order Status", "action": "order_status"},
                    "2": {"label": "প্রোডাক্ট তথ্য / Product Info", "action": "product_info"},
                    "3": {"label": "সাপোর্ট / Support", "action": "support"},
                    "4": {"label": "মানুষের সাথে কথা / Speak to Human", "action": "human_agent"},
                    "0": {"label": "পুনরায় শুনুন / Repeat", "action": "repeat"}
                },
                "timeout": 10,
                "max_attempts": 3
            },
            "order": {
                "message": "আপনার অর্ডার আইডি বলুন।\n\nPlease say your order ID.",
                "options": {},
                "timeout": 15,
                "max_attempts": 2
            },
            "product": {
                "message": "কোন প্রোডাক্ট খুঁজছেন? নাম বলুন।\n\nWhat product are you looking for? Say the name.",
                "options": {},
                "timeout": 15,
                "max_attempts": 2
            },
            "support": {
                "message": "আপনার সমস্যা বর্ণনা করুন।\n\nPlease describe your issue.",
                "options": {},
                "timeout": 20,
                "max_attempts": 2
            }
        }

    def handle_incoming_call(self, request_data: Dict[str, Any], db: Session) -> str:
        """Handle incoming Twilio call and initiate IVR flow"""
        try:
            # Extract call details
            call_sid = request_data.get('CallSid')
            from_number = request_data.get('From')
            to_number = request_data.get('To')

            logger.info(f"Incoming call from {from_number} to {to_number}, SID: {call_sid}")

            # Create IVR call record
            ivr_call = IVRCall(
                twilio_call_sid=call_sid,
                from_number=from_number,
                to_number=to_number,
                status="active",
                current_menu="main",
                call_start_time=datetime.utcnow()
            )

            # Try to find organization by phone number
            organization = self._find_organization_by_phone(to_number, db)
            if organization:
                ivr_call.organization_id = organization.id

                # Create AI conversation for the call
                conversation_id = self.ai_service.create_conversation(
                    agent_id=organization.default_ai_agent_id or 1,
                    platform="ivr",
                    user_phone=from_number,
                    db=db
                )
                ivr_call.conversation_id = conversation_id

            db.add(ivr_call)
            db.commit()

            # Generate TwiML response for main menu
            response = VoiceResponse()

            # Gather speech input with DTMF fallback
            gather = Gather(
                input='speech dtmf',
                timeout=10,
                num_digits=1,
                language='bn-BD',
                speech_timeout='auto',
                action='/api/ivr/process-input',
                method='POST'
            )

            # Add menu message in Bangla
            gather.say(
                message=self.ivr_menus["main"]["message"],
                voice='Polly.Aditi',  # Amazon Polly Bangla voice
                language='bn-IN'
            )

            response.append(gather)

            # If no input, repeat menu
            response.redirect('/api/ivr/main-menu')

            return str(response)

        except Exception as e:
            logger.error(f"Error handling incoming call: {str(e)}")
            # Return basic error response
            response = VoiceResponse()
            response.say("দুঃখিত, একটি ত্রুটি হয়েছে। অনুগ্রহ করে পরে আবার চেষ্টা করুন।", voice='Polly.Aditi', language='bn-IN')
            return str(response)

    def process_ivr_input(self, request_data: Dict[str, Any], db: Session) -> str:
        """Process user input from IVR call"""
        try:
            call_sid = request_data.get('CallSid')
            speech_result = request_data.get('SpeechResult')
            dtmf_digits = request_data.get('Digits')

            logger.info(f"Processing IVR input for call {call_sid}: Speech='{speech_result}', DTMF='{dtmf_digits}'")

            # Find the IVR call
            ivr_call = db.query(IVRCall).filter(IVRCall.twilio_call_sid == call_sid).first()
            if not ivr_call:
                return self._error_response("Call not found")

            # Update call record
            ivr_call.last_input_time = datetime.utcnow()
            ivr_call.input_attempts += 1

            # Determine user input (speech takes precedence)
            user_input = speech_result or dtmf_digits
            if not user_input:
                return self._handle_no_input(ivr_call, db)

            # Process input based on current menu
            current_menu = self.ivr_menus.get(ivr_call.current_menu, self.ivr_menus["main"])

            # Handle menu selection
            if ivr_call.current_menu == "main":
                return self._process_main_menu_selection(user_input, ivr_call, db)
            else:
                return self._process_menu_input(user_input, ivr_call, current_menu, db)

        except Exception as e:
            logger.error(f"Error processing IVR input: {str(e)}")
            return self._error_response("Processing error")

    def _process_main_menu_selection(self, user_input: str, ivr_call: IVRCall, db: Session) -> str:
        """Process main menu selection"""
        menu_options = self.ivr_menus["main"]["options"]

        # Check for DTMF input first
        if user_input in menu_options:
            action = menu_options[user_input]["action"]
            return self._execute_menu_action(action, ivr_call, db)

        # Process speech input
        user_input_lower = user_input.lower()

        # Check for keywords in Bangla/English
        if any(keyword in user_input_lower for keyword in ['অর্ডার', 'order', 'status']):
            return self._execute_menu_action("order_status", ivr_call, db)
        elif any(keyword in user_input_lower for keyword in ['প্রোডাক্ট', 'product', 'item']):
            return self._execute_menu_action("product_info", ivr_call, db)
        elif any(keyword in user_input_lower for keyword in ['সাপোর্ট', 'support', 'help']):
            return self._execute_menu_action("support", ivr_call, db)
        elif any(keyword in user_input_lower for keyword in ['মানুষ', 'human', 'agent', 'representative']):
            return self._execute_menu_action("human_agent", ivr_call, db)

        # If no match found, repeat menu
        return self._repeat_menu(ivr_call, db)

    def _execute_menu_action(self, action: str, ivr_call: IVRCall, db: Session) -> str:
        """Execute selected menu action"""
        response = VoiceResponse()

        if action == "order_status":
            ivr_call.current_menu = "order"
            gather = Gather(
                input='speech',
                timeout=15,
                language='bn-BD',
                action='/api/ivr/process-input',
                method='POST'
            )
            gather.say(
                message=self.ivr_menus["order"]["message"],
                voice='Polly.Aditi',
                language='bn-IN'
            )
            response.append(gather)

        elif action == "product_info":
            ivr_call.current_menu = "product"
            gather = Gather(
                input='speech',
                timeout=15,
                language='bn-BD',
                action='/api/ivr/process-input',
                method='POST'
            )
            gather.say(
                message=self.ivr_menus["product"]["message"],
                voice='Polly.Aditi',
                language='bn-IN'
            )
            response.append(gather)

        elif action == "support":
            ivr_call.current_menu = "support"
            gather = Gather(
                input='speech',
                timeout=20,
                language='bn-BD',
                action='/api/ivr/process-input',
                method='POST'
            )
            gather.say(
                message=self.ivr_menus["support"]["message"],
                voice='Polly.Aditi',
                language='bn-IN'
            )
            response.append(gather)

        elif action == "human_agent":
            return self._escalate_to_human(ivr_call, db)

        db.commit()
        return str(response)

    def _process_menu_input(self, user_input: str, ivr_call: IVRCall, menu_config: Dict, db: Session) -> str:
        """Process input for specific menu (order, product, support)"""
        try:
            # Send user input to AI for processing
            if ivr_call.conversation_id:
                ai_response = self.ai_service.send_message(
                    conversation_id=ivr_call.conversation_id,
                    message_text=user_input,
                    db=db
                )

                # Update IVR call record
                ivr_call.last_ai_response = ai_response
                ivr_call.ai_interactions += 1

                # Check if escalation is needed
                conversation = db.query(Conversation).filter(Conversation.id == ivr_call.conversation_id).first()
                if conversation and conversation.escalated_to_human:
                    return self._escalate_to_human(ivr_call, db)

                # Generate voice response
                response = VoiceResponse()

                # Say AI response
                response.say(
                    message=ai_response,
                    voice='Polly.Aditi',
                    language='bn-IN'
                )

                # Ask if they need more help
                gather = Gather(
                    input='speech dtmf',
                    timeout=10,
                    num_digits=1,
                    language='bn-BD',
                    action='/api/ivr/process-input',
                    method='POST'
                )
                gather.say(
                    message="আর কোনো সাহায্য চান? বলুন 'হ্যাঁ' অথবা 'না', অথবা প্রধান মেনুতে ফিরে যেতে ০ প্রেস করুন।\n\nNeed more help? Say 'yes' or 'no', or press 0 to return to main menu.",
                    voice='Polly.Aditi',
                    language='bn-IN'
                )
                response.append(gather)

                db.commit()
                return str(response)

        except Exception as e:
            logger.error(f"Error processing menu input: {str(e)}")
            return self._error_response("AI processing failed")

    def _escalate_to_human(self, ivr_call: IVRCall, db: Session) -> str:
        """Escalate call to human agent"""
        try:
            ivr_call.status = "escalated"
            ivr_call.escalated_at = datetime.utcnow()
            db.commit()

            response = VoiceResponse()

            # Inform user about escalation
            response.say(
                message="আপনাকে এখন একজন মানুষের সাথে সংযোগিত করছি। অনুগ্রহ করে অপেক্ষা করুন।\n\nConnecting you with a human agent. Please wait.",
                voice='Polly.Aditi',
                language='bn-IN'
            )

            # Try to find available agent phone number
            # For now, play hold music and provide callback option
            response.play('https://demo.twilio.com/docs/classic.mp3')  # Hold music

            # In a production system, you would:
            # 1. Check for available human agents
            # 2. Queue the call
            # 3. Connect to available agent
            # 4. Provide callback option if no agents available

            return str(response)

        except Exception as e:
            logger.error(f"Error escalating to human: {str(e)}")
            return self._error_response("Escalation failed")

    def _repeat_menu(self, ivr_call: IVRCall, db: Session) -> str:
        """Repeat current menu"""
        menu_config = self.ivr_menus.get(ivr_call.current_menu, self.ivr_menus["main"])
        ivr_call.input_attempts += 1

        # Check if max attempts reached
        if ivr_call.input_attempts >= menu_config["max_attempts"]:
            return self._escalate_to_human(ivr_call, db)

        response = VoiceResponse()
        response.say(
            message="দুঃখিত, বুঝতে পারলাম না। অনুগ্রহ করে আবার বলুন।\n\nSorry, I didn't understand. Please try again.",
            voice='Polly.Aditi',
            language='bn-IN'
        )
        response.redirect('/api/ivr/main-menu')

        db.commit()
        return str(response)

    def _handle_no_input(self, ivr_call: IVRCall, db: Session) -> str:
        """Handle case where user provides no input"""
        ivr_call.no_input_count += 1

        if ivr_call.no_input_count >= 2:
            return self._escalate_to_human(ivr_call, db)

        response = VoiceResponse()
        response.say(
            message="কোনো ইনপুট পাইনি। অনুগ্রহ করে আবার চেষ্টা করুন।\n\nNo input received. Please try again.",
            voice='Polly.Aditi',
            language='bn-IN'
        )
        response.redirect('/api/ivr/main-menu')

        db.commit()
        return str(response)

    def _error_response(self, message: str = "একটি ত্রুটি হয়েছে") -> str:
        """Generate error response"""
        response = VoiceResponse()
        response.say(
            message=f"{message}. অনুগ্রহ করে পরে আবার চেষ্টা করুন।",
            voice='Polly.Aditi',
            language='bn-IN'
        )
        response.hangup()
        return str(response)

    def _find_organization_by_phone(self, phone_number: str, db: Session) -> Optional[Organization]:
        """Find organization by phone number"""
        # This would need to be implemented based on how phone numbers are stored
        # For now, return the first organization
        return db.query(Organization).first()

    def end_call(self, call_sid: str, db: Session) -> None:
        """Handle call completion"""
        try:
            ivr_call = db.query(IVRCall).filter(IVRCall.twilio_call_sid == call_sid).first()
            if ivr_call:
                ivr_call.status = "completed"
                ivr_call.call_end_time = datetime.utcnow()
                ivr_call.call_duration = (ivr_call.call_end_time - ivr_call.call_start_time).total_seconds()
                db.commit()

                logger.info(f"Call {call_sid} completed. Duration: {ivr_call.call_duration}s")

        except Exception as e:
            logger.error(f"Error ending call {call_sid}: {str(e)}")

    def get_call_analytics(self, organization_id: int, db: Session) -> Dict[str, Any]:
        """Get analytics for IVR calls"""
        try:
            calls = db.query(IVRCall).filter(IVRCall.organization_id == organization_id).all()

            total_calls = len(calls)
            completed_calls = len([c for c in calls if c.status == "completed"])
            escalated_calls = len([c for c in calls if c.status == "escalated"])

            avg_duration = 0
            if completed_calls > 0:
                durations = [c.call_duration for c in calls if c.call_duration]
                avg_duration = sum(durations) / len(durations) if durations else 0

            return {
                "total_calls": total_calls,
                "completed_calls": completed_calls,
                "escalated_calls": escalated_calls,
                "completion_rate": (completed_calls / total_calls * 100) if total_calls > 0 else 0,
                "escalation_rate": (escalated_calls / total_calls * 100) if total_calls > 0 else 0,
                "average_duration": avg_duration
            }

        except Exception as e:
            logger.error(f"Error getting call analytics: {str(e)}")
            return {}
