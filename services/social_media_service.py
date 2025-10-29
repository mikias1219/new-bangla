import json
import requests
import os
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from accounts.models import Organization
from social_media.models import SocialMediaAccount, SocialMediaMessage, SocialMediaWebhook
from chat.models import Conversation, Message
from services.openai_service import openai_service

logger = logging.getLogger(__name__)


class SocialMediaService:
    """Unified social media integration service"""

    def __init__(self, organization):
        self.organization = organization

    def connect_facebook(self, page_id, access_token, page_name):
        """Connect Facebook page"""
        account, created = SocialMediaAccount.objects.get_or_create(
            organization=self.organization,
            platform='facebook',
            account_id=page_id,
            defaults={
                'account_name': page_name,
                'access_token': access_token,
                'display_name': page_name,
            }
        )

        if not created:
            account.access_token = access_token
            account.display_name = page_name
            account.is_active = True
            account.save()

        return account

    def connect_twitter(self, account_id, access_token, access_token_secret, account_name):
        """Connect Twitter account"""
        # Store tokens securely (you might want to encrypt these)
        token_data = {
            'access_token': access_token,
            'access_token_secret': access_token_secret
        }

        account, created = SocialMediaAccount.objects.get_or_create(
            organization=self.organization,
            platform='twitter',
            account_id=account_id,
            defaults={
                'account_name': account_name,
                'access_token': json.dumps(token_data),
                'display_name': account_name,
            }
        )

        if not created:
            account.access_token = json.dumps(token_data)
            account.display_name = account_name
            account.is_active = True
            account.save()

        return account

    def connect_instagram(self, account_id, access_token, account_name):
        """Connect Instagram account"""
        account, created = SocialMediaAccount.objects.get_or_create(
            organization=self.organization,
            platform='instagram',
            account_id=account_id,
            defaults={
                'account_name': account_name,
                'access_token': access_token,
                'display_name': account_name,
            }
        )

        if not created:
            account.access_token = access_token
            account.display_name = account_name
            account.is_active = True
            account.save()

        return account

    def connect_whatsapp(self, phone_number_id, access_token, account_name, verify_token=None):
        """Connect WhatsApp Business account"""
        account, created = SocialMediaAccount.objects.get_or_create(
            organization=self.organization,
            platform='whatsapp',
            account_id=phone_number_id,
            defaults={
                'account_name': account_name,
                'access_token': access_token,
                'display_name': account_name,
                'webhook_secret': verify_token or os.getenv('WHATSAPP_VERIFY_TOKEN', ''),
            }
        )

        if not created:
            account.access_token = access_token
            account.display_name = account_name
            account.is_active = True
            if verify_token:
                account.webhook_secret = verify_token
            account.save()

        return account

    def handle_facebook_webhook(self, data):
        """Process Facebook webhook data"""
        for entry in data.get('entry', []):
            page_id = entry.get('id')

            # Get social account
            try:
                social_account = SocialMediaAccount.objects.get(
                    platform='facebook',
                    account_id=page_id,
                    is_active=True
                )
            except SocialMediaAccount.DoesNotExist:
                continue

            # Process messaging events
            for messaging_event in entry.get('messaging', []):
                self._process_facebook_message(social_account, messaging_event)

    def handle_twitter_webhook(self, data):
        """Process Twitter webhook data"""
        # Twitter webhook handling would go here
        # This is a simplified version
        pass

    def handle_whatsapp_webhook(self, data):
        """Process WhatsApp Business API webhook data"""
        # WhatsApp webhook structure: { "object": "whatsapp_business_account", "entry": [...] }
        if not isinstance(data, dict):
            return
            
        # Find WhatsApp account by organization first
        whatsapp_accounts = SocialMediaAccount.objects.filter(
            organization=self.organization,
            platform='whatsapp',
            is_active=True
        )
        
        if not whatsapp_accounts.exists():
            return
        
        # Process entries
        entries = data.get('entry', [])
        for entry in entries:
            changes = entry.get('changes', [])
            for change in changes:
                value = change.get('value', {})
                
                # Get phone number ID from metadata or contact
                phone_number_id = value.get('metadata', {}).get('phone_number_id')
                if not phone_number_id:
                    # Try to get from contacts in messages
                    contacts = value.get('contacts', [])
                    if contacts:
                        # Get account from organization
                        social_account = whatsapp_accounts.first()
                    else:
                        continue
                else:
                    # Try to find account by phone_number_id
                    try:
                        social_account = whatsapp_accounts.get(account_id=phone_number_id)
                    except SocialMediaAccount.DoesNotExist:
                        # Use first account as fallback
                        social_account = whatsapp_accounts.first()

                # Process messages
                messages = value.get('messages', [])
                for message in messages:
                    self._process_whatsapp_message(social_account, message)
                
                # Process status updates (delivery, read, etc.)
                statuses = value.get('statuses', [])
                for status_data in statuses:
                    self._process_whatsapp_status(social_account, status_data)

    def handle_instagram_webhook(self, data):
        """Process Instagram webhook data (uses Facebook Graph API structure)"""
        if not isinstance(data, dict):
            return
            
        # Find Instagram accounts for this organization
        instagram_accounts = SocialMediaAccount.objects.filter(
            organization=self.organization,
            platform='instagram',
            is_active=True
        )
        
        if not instagram_accounts.exists():
            return
        
        # Process entries (Instagram uses same structure as Facebook)
        entries = data.get('entry', [])
        for entry in entries:
            instagram_account_id = entry.get('id')
            
            # Try to find account by ID
            try:
                social_account = instagram_accounts.get(account_id=instagram_account_id)
            except SocialMediaAccount.DoesNotExist:
                # Use first account as fallback
                social_account = instagram_accounts.first()

            # Process messaging events
            messaging_events = entry.get('messaging', [])
            for messaging_event in messaging_events:
                self._process_instagram_message(social_account, messaging_event)

    def _process_facebook_message(self, social_account, messaging_event):
        """Process individual Facebook message"""
        sender_id = messaging_event.get('sender', {}).get('id')
        recipient_id = messaging_event.get('recipient', {}).get('id')
        message_data = messaging_event.get('message', {})

        if not sender_id or not message_data:
            return

        # Skip if message is from our page
        if sender_id == social_account.account_id:
            return

        # Extract message content
        message_text = message_data.get('text', '')
        message_id = messaging_event.get('message', {}).get('mid')

        # Handle attachments
        attachments = message_data.get('attachments', [])

        # Create or get conversation
        conversation = self._get_or_create_social_conversation(
            social_account, sender_id, 'facebook', message_id
        )

        # Create social media message record
        social_message = SocialMediaMessage.objects.create(
            social_account=social_account,
            organization=social_account.organization,
            message_type='incoming',
            platform_message_id=message_id,
            sender_id=sender_id,
            content=message_text,
            conversation=conversation,
            thread_id=sender_id,
            attachments=attachments
        )

        # Process with AI if auto-reply is enabled
        if social_account.auto_reply_enabled and social_account.ai_agent:
            ai_response = self._generate_ai_response(conversation, message_text, self.organization.name)

            if ai_response:
                # Send response back to Facebook
                self._send_facebook_message(social_account, sender_id, ai_response)

                # Create outgoing message record
                SocialMediaMessage.objects.create(
                    social_account=social_account,
                    organization=social_account.organization,
                    message_type='outgoing',
                    platform_message_id=f"response_{message_id}",
                    sender_id=social_account.account_id,
                    content=ai_response,
                    conversation=conversation,
                    thread_id=sender_id,
                    ai_processed=True,
                    ai_response=ai_response
                )

    def _send_facebook_message(self, social_account, recipient_id, message_text):
        """Send message to Facebook"""
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={social_account.access_token}"

        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error sending Facebook message: {e}")
            return None

    def _get_or_create_social_conversation(self, social_account, sender_id, platform, thread_id):
        """Get or create conversation for social media interaction"""
        # Try to find existing conversation
        conversation = Conversation.objects.filter(
            organization=social_account.organization,
            social_messages__platform_message_id__startswith=f"{platform}_{sender_id}"
        ).first()

        if conversation:
            return conversation

        # Create new user if needed (anonymous social media user)
        from accounts.models import User
        username = f"social_{platform}_{sender_id}"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'is_active': False,  # Anonymous user
            }
        )

        # Create conversation
        conversation = Conversation.objects.create(
            user=user,
            organization=social_account.organization,
            ai_agent=social_account.ai_agent
        )

        return conversation

    def _generate_ai_response(self, conversation, message_text, client_name=None):
        """Generate AI response for social media message using AI agent"""
        if not conversation.ai_agent:
            return "Thank you for your message. We'll get back to you soon."

        try:
            # Get recent conversation history
            recent_messages = Message.objects.filter(
                conversation=conversation
            ).order_by('-timestamp')[:10]

            conversation_history = []
            for msg in reversed(recent_messages):
                conversation_history.append({
                    'sender': 'user' if msg.sender_type == 'user' else 'ai',
                    'content': msg.content
                })

            # Generate response using OpenAI service
            system_prompt = conversation.ai_agent.system_prompt if conversation.ai_agent else None
            
            # Get client name from organization
            if client_name:
                system_prompt = f"{system_prompt or ''} You are responding on behalf of {client_name}."
            
            ai_result = openai_service.generate_chat_response(
                message=message_text,
                conversation_history=conversation_history,
                system_prompt=system_prompt,
                client_name=client_name or self.organization.name,
                model=conversation.ai_agent.model_name if conversation.ai_agent else "gpt-4o-mini",
            )

            response_text = ai_result.get('response', '')

            # Create AI message record
            Message.objects.create(
                conversation=conversation,
                sender_type='ai',
                content=response_text,
                confidence_score=ai_result.get('confidence', 0.8),
                intent_detected=ai_result.get('detected_language', '')
            )

            return response_text

        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "Thank you for your message. Our team will respond shortly."

    def _process_whatsapp_message(self, social_account, message):
        """Process individual WhatsApp message"""
        from_id = message.get('from')
        message_id = message.get('id')
        message_type = message.get('type', 'text')
        
        if not from_id or not message_id:
            return

        # Extract message content based on type
        if message_type == 'text':
            message_text = message.get('text', {}).get('body', '')
        elif message_type == 'image' or message_type == 'video':
            message_text = f"[{message_type.upper()}] {message.get(message_type, {}).get('caption', '')}"
        else:
            message_text = f"[{message_type.upper()}]"

        # Create or get conversation
        conversation = self._get_or_create_social_conversation(
            social_account, from_id, 'whatsapp', message_id
        )

        # Create social media message record
        social_message = SocialMediaMessage.objects.create(
            social_account=social_account,
            organization=social_account.organization,
            message_type='incoming',
            platform_message_id=message_id,
            sender_id=from_id,
            content=message_text,
            conversation=conversation,
            thread_id=from_id,
            content_type=message_type,
            attachments=[message] if message_type in ['image', 'video', 'audio'] else []
        )

        # Process with AI if auto-reply is enabled
        if social_account.auto_reply_enabled and social_account.ai_agent:
            ai_response = self._generate_ai_response(conversation, message_text, self.organization.name)

            if ai_response:
                # Send response back to WhatsApp
                send_result = self._send_whatsapp_message(social_account, from_id, ai_response)

                # Create outgoing message record
                SocialMediaMessage.objects.create(
                    social_account=social_account,
                    organization=social_account.organization,
                    message_type='outgoing',
                    platform_message_id=f"response_{message_id}",
                    sender_id=social_account.account_id,
                    content=ai_response,
                    conversation=conversation,
                    thread_id=from_id,
                    ai_processed=True,
                    ai_response=ai_response
                )

    def _process_instagram_message(self, social_account, messaging_event):
        """Process individual Instagram message (similar to Facebook)"""
        sender_id = messaging_event.get('sender', {}).get('id')
        message_data = messaging_event.get('message', {})

        if not sender_id or not message_data:
            return

        # Skip if message is from our account
        if sender_id == social_account.account_id:
            return

        message_text = message_data.get('text', '')
        message_id = messaging_event.get('message', {}).get('mid')

        # Create or get conversation
        conversation = self._get_or_create_social_conversation(
            social_account, sender_id, 'instagram', message_id
        )

        # Create social media message record
        social_message = SocialMediaMessage.objects.create(
            social_account=social_account,
            organization=social_account.organization,
            message_type='incoming',
            platform_message_id=message_id,
            sender_id=sender_id,
            content=message_text,
            conversation=conversation,
            thread_id=sender_id,
        )

        # Process with AI if auto-reply is enabled
        if social_account.auto_reply_enabled and social_account.ai_agent:
            ai_response = self._generate_ai_response(conversation, message_text, self.organization.name)

            if ai_response:
                # Send response back to Instagram (via Facebook Graph API)
                self._send_instagram_message(social_account, sender_id, ai_response)

                # Create outgoing message record
                SocialMediaMessage.objects.create(
                    social_account=social_account,
                    organization=social_account.organization,
                    message_type='outgoing',
                    platform_message_id=f"response_{message_id}",
                    sender_id=social_account.account_id,
                    content=ai_response,
                    conversation=conversation,
                    thread_id=sender_id,
                    ai_processed=True,
                    ai_response=ai_response
                )

    def _send_whatsapp_message(self, social_account, recipient_id, message_text):
        """Send message via WhatsApp Business API"""
        phone_number_id = social_account.account_id
        access_token = social_account.access_token
        
        if not phone_number_id or not access_token:
            logger.error(f"WhatsApp account {social_account.id} missing credentials")
            return None
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "text",
            "text": {
                "body": message_text
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error sending WhatsApp message: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return None

    def _process_whatsapp_status(self, social_account, status_data):
        """Process WhatsApp message status updates (delivered, read, etc.)"""
        try:
            message_id = status_data.get('id')
            status_type = status_data.get('status')  # sent, delivered, read, failed
            
            # Update message status if we have the message
            try:
                message = SocialMediaMessage.objects.get(
                    social_account=social_account,
                    platform_message_id=message_id
                )
                
                if status_type == 'delivered':
                    message.delivered_at = timezone.now()
                elif status_type == 'read':
                    message.read_at = timezone.now()
                    message.is_read = True
                elif status_type == 'failed':
                    message.processed_at = timezone.now()
                
                message.save()
            except SocialMediaMessage.DoesNotExist:
                pass  # Message not found, skip
                
        except Exception as e:
            logger.error(f"Error processing WhatsApp status: {e}")

    def _send_instagram_message(self, social_account, recipient_id, message_text):
        """Send message to Instagram (uses Facebook Graph API)"""
        url = f"https://graph.facebook.com/v18.0/{social_account.account_id}/messages"

        headers = {
            'Authorization': f'Bearer {social_account.access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error sending Instagram message: {e}")
            return None

    def get_account_stats(self, social_account):
        """Get statistics for social media account"""
        today = timezone.now().date()

        # Messages today
        messages_today = SocialMediaMessage.objects.filter(
            social_account=social_account,
            received_at__date=today
        ).count()

        # AI responses today
        ai_responses_today = SocialMediaMessage.objects.filter(
            social_account=social_account,
            received_at__date=today,
            ai_processed=True
        ).count()

        # Average response time (simplified)
        avg_response_time = timedelta(minutes=5)  # Placeholder

        return {
            'messages_today': messages_today,
            'ai_responses_today': ai_responses_today,
            'avg_response_time': avg_response_time,
            'is_active': social_account.is_active
        }
