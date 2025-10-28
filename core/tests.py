from django.test import TestCase
from django.contrib.auth.models import User
from .models import Client, BanglaConversation, CallLog, BanglaIntent, AdminProfile


class ClientModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            name="Test Client",
            domain="test.com",
            contact_email="test@test.com"
        )
    
    def test_client_creation(self):
        self.assertEqual(self.client.name, "Test Client")
        self.assertEqual(self.client.domain, "test.com")
        self.assertTrue(self.client.is_active)


class BanglaConversationModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            name="Test Client",
            domain="test.com",
            contact_email="test@test.com"
        )
        self.conversation = BanglaConversation.objects.create(
            client=self.client,
            user_name="Test User",
            user_message="Hello",
            ai_response="Hi there!"
        )
    
    def test_conversation_creation(self):
        self.assertEqual(self.conversation.user_name, "Test User")
        self.assertEqual(self.conversation.user_message, "Hello")
        self.assertFalse(self.conversation.is_escalated)


class CallLogModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            name="Test Client",
            domain="test.com",
            contact_email="test@test.com"
        )
        self.call_log = CallLog.objects.create(
            client=self.client,
            caller_name="Test Caller",
            question="Test question",
            ai_text_response="Test response"
        )
    
    def test_call_log_creation(self):
        self.assertEqual(self.call_log.caller_name, "Test Caller")
        self.assertEqual(self.call_log.question, "Test question")
        self.assertEqual(self.call_log.status, "pending")


class BanglaIntentModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            name="Test Client",
            domain="test.com",
            contact_email="test@test.com"
        )
        self.intent = BanglaIntent.objects.create(
            client=self.client,
            name="Test Intent",
            training_phrase="Test phrase",
            ai_response_template="Test response"
        )
    
    def test_intent_creation(self):
        self.assertEqual(self.intent.name, "Test Intent")
        self.assertEqual(self.intent.training_phrase, "Test phrase")
        self.assertTrue(self.intent.is_active)


class AdminProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testadmin",
            email="admin@test.com",
            password="testpass123"
        )
        self.admin_profile = AdminProfile.objects.create(
            user=self.user,
            role="super_admin"
        )
    
    def test_admin_profile_creation(self):
        self.assertEqual(self.admin_profile.user.username, "testadmin")
        self.assertEqual(self.admin_profile.role, "super_admin")
        self.assertTrue(self.admin_profile.can_manage_clients)
