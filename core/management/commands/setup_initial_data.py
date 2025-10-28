from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Client, BanglaIntent, AdminProfile, SystemSettings


class Command(BaseCommand):
    help = 'Set up initial data for BanglaChatPro'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data for BanglaChatPro...')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@banglachatpro.com',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS('Created superuser: admin/admin123')
            )
            
            # Create admin profile
            AdminProfile.objects.create(
                user=admin_user,
                role='super_admin'
            )
            self.stdout.write(
                self.style.SUCCESS('Created admin profile')
            )
        else:
            self.stdout.write('Superuser already exists')
        
        # Create default client
        if not Client.objects.filter(name='Default Client').exists():
            client = Client.objects.create(
                name='Default Client',
                domain='example.com',
                contact_email='contact@example.com',
                description='Default client for testing',
                is_active=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created default client: {client.name}')
            )
        else:
            self.stdout.write('Default client already exists')
        
        # Create sample intents
        sample_intents = [
            {
                'name': 'Order Status',
                'training_phrase': 'আমার অর্ডার কখন আসবে?',
                'ai_response_template': 'আপনার অর্ডারটি প্রক্রিয়াধীন আছে। ট্র্যাকিং নম্বর: {tracking_number}। আনুমানিক ডেলিভারি: {delivery_date}।',
                'description': 'Check order status and delivery information'
            },
            {
                'name': 'Product Price',
                'training_phrase': 'এই পণ্যের দাম কত?',
                'ai_response_template': 'এই পণ্যের দাম {price} টাকা। আপনি এখনই অর্ডার করতে পারেন।',
                'description': 'Get product pricing information'
            },
            {
                'name': 'Delivery Charge',
                'training_phrase': 'ডেলিভারি চার্জ কত?',
                'ai_response_template': 'ডেলিভারি চার্জ {delivery_charge} টাকা। {free_delivery_amount} টাকার বেশি অর্ডারে ফ্রি ডেলিভারি।',
                'description': 'Get delivery charge information'
            },
            {
                'name': 'Refund Policy',
                'training_phrase': 'রিফান্ড পলিসি কি?',
                'ai_response_template': 'আমাদের রিফান্ড পলিসি: {refund_policy}। রিফান্ডের জন্য {refund_time} দিন সময় আছে।',
                'description': 'Get refund policy information'
            },
            {
                'name': 'Contact Support',
                'training_phrase': 'সাপোর্টে যোগাযোগ করতে চাই',
                'ai_response_template': 'আমাদের সাপোর্ট টিমের সাথে যোগাযোগ করুন। ফোন: {phone}, ইমেইল: {email}।',
                'description': 'Contact customer support'
            }
        ]
        
        client = Client.objects.first()
        created_intents = 0
        
        for intent_data in sample_intents:
            if not BanglaIntent.objects.filter(
                client=client, 
                name=intent_data['name']
            ).exists():
                BanglaIntent.objects.create(
                    client=client,
                    **intent_data
                )
                created_intents += 1
        
        if created_intents > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Created {created_intents} sample intents')
            )
        else:
            self.stdout.write('Sample intents already exist')
        
        # Create system settings
        system_settings = [
            {
                'key': 'OPENAI_API_KEY',
                'value': 'your-openai-api-key-here',
                'description': 'OpenAI API key for AI responses',
                'data_type': 'string'
            },
            {
                'key': 'DEFAULT_AI_MODEL',
                'value': 'gpt-4o-mini',
                'description': 'Default AI model to use',
                'data_type': 'string'
            },
            {
                'key': 'AI_TEMPERATURE',
                'value': '0.7',
                'description': 'AI response creativity (0-2)',
                'data_type': 'string'
            },
            {
                'key': 'MAX_AI_RESPONSES_BEFORE_HANDOFF',
                'value': '2',
                'description': 'Maximum AI responses before human handoff',
                'data_type': 'integer'
            },
            {
                'key': 'AUTO_DELETE_OLD_LOGS_DAYS',
                'value': '90',
                'description': 'Days after which to auto-delete old logs',
                'data_type': 'integer'
            },
            {
                'key': 'GDPR_COMPLIANCE',
                'value': 'True',
                'description': 'Enable GDPR compliance features',
                'data_type': 'boolean'
            },
            {
                'key': 'ENABLE_VOICE_CHAT',
                'value': 'True',
                'description': 'Enable voice chat functionality',
                'data_type': 'boolean'
            },
            {
                'key': 'ENABLE_SOCIAL_MEDIA',
                'value': 'True',
                'description': 'Enable social media integration',
                'data_type': 'boolean'
            }
        ]
        
        created_settings = 0
        for setting_data in system_settings:
            if not SystemSettings.objects.filter(key=setting_data['key']).exists():
                SystemSettings.objects.create(**setting_data)
                created_settings += 1
        
        if created_settings > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Created {created_settings} system settings')
            )
        else:
            self.stdout.write('System settings already exist')
        
        self.stdout.write(
            self.style.SUCCESS('Initial data setup completed successfully!')
        )
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Set your OpenAI API key in the admin dashboard')
        self.stdout.write('2. Create additional clients as needed')
        self.stdout.write('3. Customize AI intents for your business')
        self.stdout.write('4. Test the chat interface')
        self.stdout.write('')
        self.stdout.write('Access the admin dashboard at: /admin-dashboard/')
        self.stdout.write('Username: admin, Password: admin123')
