import os
import requests
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import AIAgent, Conversation, Message
from .ai_chat import AIChatService
import logging

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for WhatsApp Business API integration"""

    def __init__(self):
        self.api_version = "v17.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "your_verify_token_here")
        self.ai_chat_service = AIChatService()

    def verify_webhook(self, hub_mode: str, hub_challenge: str, hub_verify_token: str) -> Optional[str]:
        """Verify WhatsApp webhook"""
        if hub_mode == "subscribe" and hub_verify_token == self.verify_token:
            logger.info("WhatsApp webhook verified successfully")
            return hub_challenge
        else:
            logger.warning("WhatsApp webhook verification failed")
            return None

    def process_webhook(self, data: Dict[str, Any], db: Session) -> bool:
        """Process incoming WhatsApp webhook messages"""
        try:
            if "object" not in data or data["object"] != "whatsapp_business_account":
                return False

            entries = data.get("entry", [])
            for entry in entries:
                changes = entry.get("changes", [])
                for change in changes:
                    if change.get("field") == "messages":
                        messages = change.get("value", {}).get("messages", [])
                        for message in messages:
                            self._process_message(message, db)

            return True

        except Exception as e:
            logger.error(f"Error processing WhatsApp webhook: {str(e)}")
            return False

    def _process_message(self, message: Dict[str, Any], db: Session):
        """Process a single WhatsApp message"""
        try:
            message_id = message.get("id")
            from_number = message.get("from")
            message_type = message.get("type")
            timestamp = message.get("timestamp")

            # Find AI agent by phone number
            agent = db.query(AIAgent).filter(
                AIAgent.whatsapp_number == from_number
            ).first()

            if not agent:
                logger.info(f"No AI agent found for WhatsApp number: {from_number}")
                return

            # Handle different message types
            if message_type == "text":
                text_content = message.get("text", {}).get("body", "")
                self._handle_text_message(agent, from_number, text_content, db)

            elif message_type == "image":
                # Handle image messages (could extract text using OCR)
                self._send_whatsapp_message(
                    from_number,
                    "I received your image, but I can only process text messages for now.",
                    db
                )

            # Mark message as read
            self._mark_message_read(message_id)

        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {str(e)}")

    def _handle_text_message(self, agent: AIAgent, from_number: str, text: str, db: Session):
        """Handle incoming text message"""
        try:
            # Find or create conversation
            conversation = db.query(Conversation).filter(
                Conversation.whatsapp_conversation_id == from_number,
                Conversation.ai_agent_id == agent.id
            ).first()

            if not conversation:
                conversation_id = self.ai_chat_service.create_conversation(
                    agent_id=agent.id,
                    platform="whatsapp",
                    user_phone=from_number,
                    db=db
                )
                conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()

            if not conversation:
                logger.error("Failed to create WhatsApp conversation")
                return

            # Get AI response
            response = self.ai_chat_service.send_message(conversation.id, text, db)

            if response:
                # Send response back via WhatsApp
                self._send_whatsapp_message(from_number, response, db)
            else:
                # Send error message
                self._send_whatsapp_message(
                    from_number,
                    "I'm sorry, I'm having trouble processing your message right now. Please try again later.",
                    db
                )

        except Exception as e:
            logger.error(f"Error handling WhatsApp text message: {str(e)}")
            self._send_whatsapp_message(
                from_number,
                "I'm sorry, something went wrong. Please try again later.",
                db
            )

    def _send_whatsapp_message(self, to_number: str, message: str, db: Session) -> bool:
        """Send a message via WhatsApp Business API"""
        try:
            if not self.access_token or not self.phone_number_id:
                logger.error("WhatsApp credentials not configured")
                return False

            url = f"{self.base_url}/{self.phone_number_id}/messages"

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                logger.info(f"WhatsApp message sent successfully to {to_number}")
                return True
            else:
                logger.error(f"Failed to send WhatsApp message: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return False

    def _mark_message_read(self, message_id: str):
        """Mark a message as read"""
        try:
            if not self.access_token or not self.phone_number_id:
                return

            url = f"{self.base_url}/{self.phone_number_id}/messages"

            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code != 200:
                logger.warning(f"Failed to mark message as read: {response.status_code}")

        except Exception as e:
            logger.error(f"Error marking message as read: {str(e)}")

    def send_template_message(self, to_number: str, template_name: str, language_code: str = "en") -> bool:
        """Send a WhatsApp template message"""
        try:
            if not self.access_token or not self.phone_number_id:
                logger.error("WhatsApp credentials not configured")
                return False

            url = f"{self.base_url}/{self.phone_number_id}/messages"

            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    }
                }
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                logger.info(f"WhatsApp template message sent successfully to {to_number}")
                return True
            else:
                logger.error(f"Failed to send WhatsApp template message: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending WhatsApp template message: {str(e)}")
            return False

    def get_phone_number_info(self) -> Optional[Dict[str, Any]]:
        """Get WhatsApp Business Account phone number information"""
        try:
            if not self.access_token or not self.phone_number_id:
                return None

            url = f"{self.base_url}/{self.phone_number_id}"

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get phone number info: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting phone number info: {str(e)}")
            return None
