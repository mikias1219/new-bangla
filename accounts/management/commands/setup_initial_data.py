from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Organization, APIKey
from chat.models import AIAgent, Intent
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up initial data for BanglaChatPro'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data for BanglaChatPro...')

        # Create organization
        organization, created = Organization.objects.get_or_create(
            name='BanglaChatPro Demo',
            defaults={
                'description': 'Demo organization for BanglaChatPro',
                'website': 'https://bdchatpro.com',
                'subscription_plan': 'premium',
                'contact_email': 'admin@bdchatpro.com',
                'max_users': 100,
                'max_conversations': 5000,
                'is_active': True,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created organization: {organization.name}'))
        else:
            self.stdout.write(f'Organization already exists: {organization.name}')

        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@bdchatpro.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_admin': True,
                'is_staff': True,
                'is_superuser': True,
                'organization': organization,
            }
        )

        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_user.username}'))
        else:
            self.stdout.write(f'Admin user already exists: {admin_user.username}')

        # Create client user
        client_user, created = User.objects.get_or_create(
            username='client',
            defaults={
                'email': 'client@bdchatpro.com',
                'first_name': 'Demo',
                'last_name': 'Client',
                'is_admin': False,
                'organization': organization,
            }
        )

        if created:
            client_user.set_password('client123')
            client_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created client user: {client_user.username}'))
        else:
            self.stdout.write(f'Client user already exists: {client_user.username}')

        # Create API Key for OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            api_key, created = APIKey.objects.get_or_create(
                organization=organization,
                name='OpenAI API Key',
                defaults={
                    'key': openai_key,
                    'provider': 'openai',
                    'is_active': True,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created OpenAI API key'))
            else:
                self.stdout.write(f'OpenAI API key already exists')
        else:
            self.stdout.write(self.style.WARNING('OPENAI_API_KEY not found in environment'))

        # Create AI Agent
        ai_agent, created = AIAgent.objects.get_or_create(
            organization=organization,
            name='BanglaChat Assistant',
            defaults={
                'description': 'AI assistant for BanglaChatPro customer support',
                'status': 'active',
                'model_provider': 'openai',
                'model_name': 'gpt-3.5-turbo',
                'system_prompt': '''You are a helpful AI assistant for BanglaChatPro, a customer service platform.
                You help users with their questions and provide accurate, helpful responses.
                Always be polite, professional, and concise in your responses.
                If you cannot help with something, suggest contacting a human agent.''',
                'temperature': 0.7,
                'max_tokens': 1000,
                'supported_languages': ['en', 'bn'],
                'primary_language': 'en',
                'voice_enabled': True,
                'max_consecutive_responses': 3,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created AI Agent: {ai_agent.name}'))
        else:
            self.stdout.write(f'AI Agent already exists: {ai_agent.name}')

        # Create sample intents
        intents_data = [
            {
                'name': 'greeting',
                'description': 'User greeting and introduction',
                'examples': ['hello', 'hi there', 'good morning', 'how are you'],
                'responses': ['Hello! How can I help you today?', 'Hi there! Welcome to BanglaChatPro. What can I assist you with?'],
            },
            {
                'name': 'pricing_inquiry',
                'description': 'Questions about pricing and plans',
                'examples': ['how much does it cost', 'what are your prices', 'pricing plans', 'subscription costs'],
                'responses': ['We offer flexible pricing plans starting from our Free tier. Would you like me to explain our different plans?', 'Our pricing depends on your needs. Let me tell you about our available plans.'],
            },
            {
                'name': 'technical_support',
                'description': 'Technical issues and support requests',
                'examples': ['having trouble', 'not working', 'error message', 'technical problem'],
                'responses': ['I\'m sorry to hear you\'re experiencing issues. Can you please describe the problem in more detail?', 'Let me help you troubleshoot this issue. What exactly is happening?'],
            },
        ]

        for intent_data in intents_data:
            intent, created = Intent.objects.get_or_create(
                ai_agent=ai_agent,
                name=intent_data['name'],
                defaults={
                    'description': intent_data['description'],
                    'examples': intent_data['examples'],
                    'responses': intent_data['responses'],
                    'confidence_threshold': 0.8,
                    'is_active': True,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created intent: {intent.name}'))
            else:
                self.stdout.write(f'Intent already exists: {intent.name}')

        self.stdout.write(self.style.SUCCESS('Initial data setup completed successfully!'))
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write(f'Admin: admin / admin123')
        self.stdout.write(f'Client: client / client123')
        self.stdout.write('')
        self.stdout.write('URLs:')
        self.stdout.write('Admin panel: https://bdchatpro.com/admin/')
        self.stdout.write('Dashboard: https://bdchatpro.com/accounts/login/')
