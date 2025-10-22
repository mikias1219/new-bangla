import os
import requests
import json
import hmac
import hashlib
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import AIAgent, Conversation, Message
from .ai_chat import AIChatService
import logging

logger = logging.getLogger(__name__)

class InstagramService:
    """Service for Instagram Business Messaging integration"""

    def __init__(self):
        self.api_version = "v17.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET")  # Same as Facebook
        self.verify_token = os.getenv("INSTAGRAM_VERIFY_TOKEN", "your_verify_token_here")
        self.ai_chat_service = AIChatService()

    def verify_webhook(self, hub_mode: str, hub_challenge: str, hub_verify_token: str) -> Optional[str]:
        """Verify Instagram webhook"""
        if hub_mode == "subscribe" and hub_verify_token == self.verify_token:
            logger.info("Instagram webhook verified successfully")
            return hub_challenge
        else:
            logger.warning("Instagram webhook verification failed")
            return None

    def verify_signature(self, request_body: str, signature: str) -> bool:
        """Verify Instagram webhook signature"""
        if not self.app_secret:
            logger.warning("Facebook app secret not configured")
            return False

        expected_signature = hmac.new(
            self.app_secret.encode('utf-8'),
            request_body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Facebook sends signature as "sha256=..."
        expected_signature = f"sha256={expected_signature}"

        return hmac.compare_digest(expected_signature, signature)

    def process_webhook(self, data: Dict[str, Any], db: Session) -> bool:
        """Process incoming Instagram webhook messages"""
        try:
            if "object" not in data or data["object"] != "instagram":
                return False

            entries = data.get("entry", [])
            for entry in entries:
                messaging_events = entry.get("messaging", [])

                for event in messaging_events:
                    if "message" in event:
                        self._process_message(event, db)

            return True

        except Exception as e:
            logger.error(f"Error processing Instagram webhook: {str(e)}")
            return False

    def _process_message(self, event: Dict[str, Any], db: Session):
        """Process a single Instagram message"""
        try:
            sender_id = event.get("sender", {}).get("id")
            recipient_id = event.get("recipient", {}).get("id")
            message = event.get("message", {})
            message_text = message.get("text", "")

            if not sender_id or not message_text:
                return

            # Find AI agent by Instagram account ID
            agent = db.query(AIAgent).filter(
                AIAgent.instagram_account_id == recipient_id
            ).first()

            if not agent:
                logger.info(f"No AI agent found for Instagram account: {recipient_id}")
                return

            self._handle_text_message(agent, sender_id, message_text, db)

        except Exception as e:
            logger.error(f"Error processing Instagram message: {str(e)}")

    def _handle_text_message(self, agent: AIAgent, sender_id: str, text: str, db: Session):
        """Handle incoming text message"""
        try:
            # Find or create conversation
            conversation = db.query(Conversation).filter(
                Conversation.instagram_conversation_id == sender_id,
                Conversation.ai_agent_id == agent.id
            ).first()

            if not conversation:
                conversation_id = self.ai_chat_service.create_conversation(
                    agent_id=agent.id,
                    platform="instagram",
                    user_email=f"{sender_id}@instagram.com",  # Placeholder email
                    db=db
                )
                conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()

            if not conversation:
                logger.error("Failed to create Instagram conversation")
                return

            # Get AI response
            response = self.ai_chat_service.send_message(conversation.id, text, db)

            if response:
                # Send response back via Instagram
                self._send_instagram_message(sender_id, response)
            else:
                # Send error message
                self._send_instagram_message(
                    sender_id,
                    "I'm sorry, I'm having trouble processing your message right now. Please try again later."
                )

        except Exception as e:
            logger.error(f"Error handling Instagram text message: {str(e)}")
            self._send_instagram_message(
                sender_id,
                "I'm sorry, something went wrong. Please try again later."
            )

    def _send_instagram_message(self, recipient_id: str, message: str) -> bool:
        """Send a message via Instagram Business Messaging API"""
        try:
            if not self.access_token:
                logger.error("Instagram access token not configured")
                return False

            url = f"{self.base_url}/me/messages"

            payload = {
                "recipient": {
                    "id": recipient_id
                },
                "message": {
                    "text": message
                }
            }

            params = {
                "access_token": self.access_token
            }

            response = requests.post(url, json=payload, params=params, timeout=30)

            if response.status_code == 200:
                logger.info(f"Instagram message sent successfully to {recipient_id}")
                return True
            else:
                logger.error(f"Failed to send Instagram message: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending Instagram message: {str(e)}")
            return False

    def send_quick_replies(self, recipient_id: str, text: str, quick_replies: list) -> bool:
        """Send a message with quick replies"""
        try:
            if not self.access_token:
                logger.error("Instagram access token not configured")
                return False

            url = f"{self.base_url}/me/messages"

            payload = {
                "recipient": {
                    "id": recipient_id
                },
                "message": {
                    "text": text,
                    "quick_replies": quick_replies
                }
            }

            params = {
                "access_token": self.access_token
            }

            response = requests.post(url, json=payload, params=params, timeout=30)

            if response.status_code == 200:
                logger.info(f"Instagram quick replies sent successfully to {recipient_id}")
                return True
            else:
                logger.error(f"Failed to send Instagram quick replies: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending Instagram quick replies: {str(e)}")
            return False

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get Instagram user profile information"""
        try:
            if not self.access_token:
                return None

            url = f"{self.base_url}/{user_id}"

            params = {
                "fields": "username,name,profile_pic",
                "access_token": self.access_token
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user profile: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return None

    def get_instagram_account_info(self) -> Optional[Dict[str, Any]]:
        """Get Instagram Business Account information"""
        try:
            if not self.access_token:
                return None

            url = f"{self.base_url}/me"

            params = {
                "fields": "id,username,name,profile_picture_url,ig_id",
                "access_token": self.access_token
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get Instagram account info: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting Instagram account info: {str(e)}")
            return None
