import json
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from accounts.models import Organization
from social_media.models import SocialMediaAccount, SocialMediaMessage, SocialMediaWebhook
from chat.models import Conversation, Message
from services.openai_service import OpenAIService


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
            ai_response = self._generate_ai_response(conversation, message_text)

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

    def _generate_ai_response(self, conversation, message_text):
        """Generate AI response for social media message"""
        if not conversation.ai_agent:
            return "Thank you for your message. We'll get back to you soon."

        try:
            openai_service = OpenAIService(conversation.organization)

            # Get recent conversation history
            recent_messages = Message.objects.filter(
                conversation=conversation
            ).order_by('-timestamp')[:5]

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
                "content": message_text
            })

            # Generate response
            ai_response = openai_service.generate_chat_response(
                messages=conversation_history,
                ai_agent=conversation.ai_agent
            )

            response_text = ai_response.get('content', '')

            # Create AI message record
            Message.objects.create(
                conversation=conversation,
                sender_type='ai',
                content=response_text,
                confidence_score=ai_response.get('confidence', 0.8)
            )

            return response_text

        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "Thank you for your message. Our team will respond shortly."

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
