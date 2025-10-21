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

class FacebookService:
    """Service for Facebook Messenger integration"""

    def __init__(self):
        self.api_version = "v17.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self.verify_token = os.getenv("FACEBOOK_VERIFY_TOKEN", "your_verify_token_here")
        self.ai_chat_service = AIChatService()

    def verify_webhook(self, hub_mode: str, hub_challenge: str, hub_verify_token: str) -> Optional[str]:
        """Verify Facebook webhook"""
        if hub_mode == "subscribe" and hub_verify_token == self.verify_token:
            logger.info("Facebook webhook verified successfully")
            return hub_challenge
        else:
            logger.warning("Facebook webhook verification failed")
            return None

    def verify_signature(self, request_body: str, signature: str) -> bool:
        """Verify Facebook webhook signature"""
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
        """Process incoming Facebook webhook messages"""
        try:
            if "object" not in data or data["object"] != "page":
                return False

            entries = data.get("entry", [])
            for entry in entries:
                page_id = entry.get("id")
                messaging_events = entry.get("messaging", [])

                for event in messaging_events:
                    if "message" in event:
                        self._process_message(event, page_id, db)

            return True

        except Exception as e:
            logger.error(f"Error processing Facebook webhook: {str(e)}")
            return False

    def _process_message(self, event: Dict[str, Any], page_id: str, db: Session):
        """Process a single Facebook message"""
        try:
            sender_id = event.get("sender", {}).get("id")
            recipient_id = event.get("recipient", {}).get("id")
            message = event.get("message", {})
            message_text = message.get("text", "")

            if not sender_id or not message_text:
                return

            # Find AI agent by page ID
            agent = db.query(AIAgent).filter(
                AIAgent.facebook_page_id == page_id
            ).first()

            if not agent:
                logger.info(f"No AI agent found for Facebook page: {page_id}")
                return

            # Skip messages from the page itself
            if sender_id == page_id:
                return

            self._handle_text_message(agent, sender_id, message_text, db)

        except Exception as e:
            logger.error(f"Error processing Facebook message: {str(e)}")

    def _handle_text_message(self, agent: AIAgent, sender_id: str, text: str, db: Session):
        """Handle incoming text message"""
        try:
            # Find or create conversation
            conversation = db.query(Conversation).filter(
                Conversation.facebook_conversation_id == sender_id,
                Conversation.ai_agent_id == agent.id
            ).first()

            if not conversation:
                conversation_id = self.ai_chat_service.create_conversation(
                    agent_id=agent.id,
                    platform="facebook",
                    user_email=f"{sender_id}@facebook.com",  # Placeholder email
                    db=db
                )
                conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()

            if not conversation:
                logger.error("Failed to create Facebook conversation")
                return

            # Get AI response
            response = self.ai_chat_service.send_message(conversation.id, text, db)

            if response:
                # Send response back via Facebook
                self._send_facebook_message(sender_id, response)
            else:
                # Send error message
                self._send_facebook_message(
                    sender_id,
                    "I'm sorry, I'm having trouble processing your message right now. Please try again later."
                )

        except Exception as e:
            logger.error(f"Error handling Facebook text message: {str(e)}")
            self._send_facebook_message(
                sender_id,
                "I'm sorry, something went wrong. Please try again later."
            )

    def _send_facebook_message(self, recipient_id: str, message: str) -> bool:
        """Send a message via Facebook Messenger API"""
        try:
            if not self.access_token:
                logger.error("Facebook access token not configured")
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
                logger.info(f"Facebook message sent successfully to {recipient_id}")
                return True
            else:
                logger.error(f"Failed to send Facebook message: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending Facebook message: {str(e)}")
            return False

    def send_quick_replies(self, recipient_id: str, text: str, quick_replies: list) -> bool:
        """Send a message with quick replies"""
        try:
            if not self.access_token:
                logger.error("Facebook access token not configured")
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
                logger.info(f"Facebook quick replies sent successfully to {recipient_id}")
                return True
            else:
                logger.error(f"Failed to send Facebook quick replies: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending Facebook quick replies: {str(e)}")
            return False

    def send_generic_template(self, recipient_id: str, elements: list) -> bool:
        """Send a generic template message"""
        try:
            if not self.access_token:
                logger.error("Facebook access token not configured")
                return False

            url = f"{self.base_url}/me/messages"

            payload = {
                "recipient": {
                    "id": recipient_id
                },
                "message": {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "generic",
                            "elements": elements
                        }
                    }
                }
            }

            params = {
                "access_token": self.access_token
            }

            response = requests.post(url, json=payload, params=params, timeout=30)

            if response.status_code == 200:
                logger.info(f"Facebook template sent successfully to {recipient_id}")
                return True
            else:
                logger.error(f"Failed to send Facebook template: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending Facebook template: {str(e)}")
            return False

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get Facebook user profile information"""
        try:
            if not self.access_token:
                return None

            url = f"{self.base_url}/{user_id}"

            params = {
                "fields": "first_name,last_name,profile_pic",
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

    def set_welcome_message(self, page_id: str, message: str) -> bool:
        """Set the welcome message for the page"""
        try:
            if not self.access_token:
                logger.error("Facebook access token not configured")
                return False

            url = f"{self.base_url}/me/messenger_profile"

            payload = {
                "greeting": [
                    {
                        "locale": "default",
                        "text": message
                    }
                ]
            }

            params = {
                "access_token": self.access_token
            }

            response = requests.post(url, json=payload, params=params, timeout=30)

            if response.status_code == 200:
                logger.info(f"Welcome message set successfully for page {page_id}")
                return True
            else:
                logger.error(f"Failed to set welcome message: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error setting welcome message: {str(e)}")
            return False

    def set_get_started_button(self, page_id: str, payload: str = "GET_STARTED") -> bool:
        """Set the Get Started button for the page"""
        try:
            if not self.access_token:
                logger.error("Facebook access token not configured")
                return False

            url = f"{self.base_url}/me/messenger_profile"

            payload_data = {
                "get_started": {
                    "payload": payload
                }
            }

            params = {
                "access_token": self.access_token
            }

            response = requests.post(url, json=payload_data, params=params, timeout=30)

            if response.status_code == 200:
                logger.info(f"Get Started button set successfully for page {page_id}")
                return True
            else:
                logger.error(f"Failed to set Get Started button: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error setting Get Started button: {str(e)}")
            return False
