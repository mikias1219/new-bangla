import os
import json
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from django.conf import settings
from django.utils import timezone
from accounts.models import APIKey, Organization
from chat.models import Conversation, Message, AIAgent
from voice.models import VoiceRecording, VoiceSession
from services.openai_service import OpenAIService


class TwilioService:
    """Twilio integration for voice calls and SMS"""

    def __init__(self, organization):
        self.organization = organization
        self.client = None
        self.api_key = None

        # Get Twilio credentials
        try:
            self.api_key = APIKey.objects.get(
                organization=organization,
                provider='twilio',
                is_active=True
            )
            account_sid = self.api_key.key
            auth_token = self.api_key.name  # Using name field for auth token

            if account_sid and auth_token:
                self.client = Client(account_sid, auth_token)
        except APIKey.DoesNotExist:
            raise ValueError(f"Twilio API key not configured for organization {organization.name}")

    def make_call(self, to_number, from_number=None, twiml_url=None):
        """Initiate an outbound call"""
        if not self.client:
            raise ValueError("Twilio client not initialized")

        # Use organization's phone number or default
        if not from_number:
            from_number = getattr(self.organization, 'phone_number', None) or os.getenv('TWILIO_PHONE_NUMBER')

        if not from_number:
            raise ValueError("No phone number configured for outgoing calls")

        # Create TwiML URL if not provided
        if not twiml_url:
            twiml_url = f"{settings.SITE_URL}/voice/twiml/{self.organization.id}/"

        call = self.client.calls.create(
            to=to_number,
            from_=from_number,
            url=twiml_url,
            method='POST'
        )

        return call.sid

    def generate_twiml(self, request_data, organization_id):
        """Generate TwiML response for voice calls"""
        response = VoiceResponse()

        # Get call details
        call_sid = request_data.get('CallSid')
        from_number = request_data.get('From')

        # Find or create conversation
        conversation = self._get_or_create_voice_conversation(from_number, organization_id)

        # Create voice session
        voice_session = VoiceSession.objects.create(
            conversation=conversation,
            user=conversation.user,
            session_id=call_sid,
        )

        # Initial greeting
        response.say("Hello! You've reached our AI assistant. Please say something after the beep.", voice='alice')

        # Gather speech input
        gather = Gather(
            input='speech',
            action=f'/voice/process/{organization_id}/',
            method='POST',
            timeout=5,
            speech_timeout='auto'
        )
        gather.say("Go ahead, I'm listening.", voice='alice')
        response.append(gather)

        # If no speech detected, repeat
        response.say("I didn't hear anything. Goodbye!", voice='alice')
        response.hangup()

        return str(response)

    def process_speech(self, request_data, organization_id):
        """Process speech input from Twilio"""
        response = VoiceResponse()
        call_sid = request_data.get('CallSid')
        speech_result = request_data.get('SpeechResult')

        if not speech_result:
            # No speech detected
            response.say("I didn't catch that. Please try again.", voice='alice')
            gather = Gather(
                input='speech',
                action=f'/voice/process/{organization_id}/',
                method='POST',
                timeout=5
            )
            gather.say("Go ahead, I'm listening.", voice='alice')
            response.append(gather)
            response.hangup()
            return str(response)

        try:
            # Get voice session
            voice_session = VoiceSession.objects.get(session_id=call_sid)
            conversation = voice_session.conversation

            # Create user message
            user_message = Message.objects.create(
                conversation=conversation,
                sender_type='user',
                sender=conversation.user,
                content=f"Voice: {speech_result}",
                content_type='voice'
            )

            # Process with AI
            ai_response_text = self._process_with_ai(conversation, speech_result)

            # Create AI message
            ai_message = Message.objects.create(
                conversation=conversation,
                sender_type='ai',
                content=ai_response_text,
                confidence_score=0.85
            )

            # Generate speech response
            speech_url = self._generate_speech_response(ai_response_text, conversation.organization)

            # Play AI response
            response.play(speech_url)

            # Continue conversation
            gather = Gather(
                input='speech',
                action=f'/voice/process/{organization_id}/',
                method='POST',
                timeout=5
            )
            gather.say("How can I help you further?", voice='alice')
            response.append(gather)

            # Update session
            voice_session.total_recordings += 1
            voice_session.save()

        except Exception as e:
            response.say(f"I'm sorry, there was an error: {str(e)}", voice='alice')
            response.hangup()

        return str(response)

    def send_sms(self, to_number, message, from_number=None):
        """Send SMS message"""
        if not self.client:
            raise ValueError("Twilio client not initialized")

        if not from_number:
            from_number = getattr(self.organization, 'phone_number', None) or os.getenv('TWILIO_PHONE_NUMBER')

        if not from_number:
            raise ValueError("No phone number configured for SMS")

        message = self.client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )

        return message.sid

    def _get_or_create_voice_conversation(self, from_number, organization_id):
        """Get or create conversation for voice call"""
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise ValueError("Organization not found")

        # Try to find existing user by phone number
        user = None
        if hasattr(organization, 'users'):
            user = organization.users.filter(phone=from_number).first()

        if not user:
            # Create anonymous user for this call
            from accounts.models import User
            user = User.objects.create(
                username=f"voice_call_{from_number}_{timezone.now().timestamp()}",
                phone=from_number,
                is_active=False  # Mark as inactive until they register
            )
            organization.users.add(user)

        # Create conversation
        conversation = Conversation.objects.create(
            user=user,
            organization=organization,
            ai_agent=AIAgent.objects.filter(organization=organization, voice_enabled=True).first()
        )

        return conversation

    def _process_with_ai(self, conversation, speech_text):
        """Process speech with AI assistant"""
        if not conversation.ai_agent:
            return "I'm sorry, no AI agent is configured for voice calls."

        try:
            openai_service = OpenAIService(conversation.organization)

            # Get conversation history
            recent_messages = Message.objects.filter(
                conversation=conversation
            ).order_by('-timestamp')[:10]

            conversation_history = []
            for msg in reversed(recent_messages):
                role = "assistant" if msg.sender_type == "ai" else "user"
                conversation_history.append({
                    "role": role,
                    "content": msg.content
                })

            # Add current message
            conversation_history.append({
                "role": "user",
                "content": speech_text
            })

            # Generate AI response
            ai_response = openai_service.generate_chat_response(
                messages=conversation_history,
                ai_agent=conversation.ai_agent
            )

            return ai_response.get('content', 'I apologize, but I could not generate a response.')

        except Exception as e:
            return f"I'm sorry, there was an error processing your request: {str(e)}"

    def _generate_speech_response(self, text, organization):
        """Generate speech from text using OpenAI TTS"""
        try:
            openai_service = OpenAIService(organization)
            speech_url = openai_service.generate_speech(text)

            return speech_url

        except Exception as e:
            # Fallback to simple text response
            return f"I'm sorry, I couldn't generate speech: {str(e)}"
