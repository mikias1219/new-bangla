from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Conversation(models.Model):
    """Chat conversation model"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('transferred', 'Transferred to Human'),
        ('abandoned', 'Abandoned'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations')
    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE, related_name='conversations')

    # Conversation metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    title = models.CharField(max_length=255, blank=True, help_text="Auto-generated conversation title")

    # AI Agent assigned
    ai_agent = models.ForeignKey('AIAgent', on_delete=models.SET_NULL, null=True, blank=True)

    # Transfer information
    transferred_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='transferred_conversations')
    transfer_reason = models.TextField(blank=True)

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Statistics
    message_count = models.PositiveIntegerField(default=0)
    ai_responses = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Conversation')
        verbose_name_plural = _('Conversations')
        ordering = ['-last_message_at']

    def __str__(self):
        return f"Conversation {self.id} - {self.user.username}"

    @property
    def duration(self):
        """Calculate conversation duration"""
        end_time = self.completed_at or self.last_message_at
        return end_time - self.started_at


class Message(models.Model):
    """Individual message in a conversation"""

    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI Agent'),
        ('human', 'Human Agent'),
        ('system', 'System'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=10, choices=SENDER_CHOICES)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    # Message content
    content = models.TextField()
    content_type = models.CharField(max_length=20, default='text', choices=[
        ('text', 'Text'),
        ('voice', 'Voice'),
        ('file', 'File'),
    ])

    # Voice/file attachments
    voice_recording = models.FileField(upload_to='voice_recordings/', blank=True, null=True)
    file_attachment = models.FileField(upload_to='attachments/', blank=True, null=True)

    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # AI response metadata
    confidence_score = models.FloatField(null=True, blank=True, help_text="AI confidence in response")
    intent_detected = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender_type}: {self.content[:50]}..."


class AIAgent(models.Model):
    """AI Agent configuration"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('training', 'Training'),
    ]

    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE, related_name='ai_agents')

    # Basic information
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='ai_avatars/', blank=True, null=True)

    # Configuration
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    model_provider = models.CharField(max_length=50, choices=[
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('google', 'Google AI'),
        ('azure', 'Azure OpenAI'),
    ], default='openai')

    model_name = models.CharField(max_length=100, default='gpt-3.5-turbo')

    # Personality and behavior
    system_prompt = models.TextField(help_text="System prompt defining AI personality and behavior")
    temperature = models.FloatField(default=0.7, help_text="Creativity/randomness (0-2)")
    max_tokens = models.PositiveIntegerField(default=1000)

    # Language support
    supported_languages = models.JSONField(default=list, help_text="List of supported languages")
    primary_language = models.CharField(max_length=10, default='en')

    # Capabilities
    voice_enabled = models.BooleanField(default=False)
    file_processing = models.BooleanField(default=False)

    # Handoff settings
    max_consecutive_responses = models.PositiveIntegerField(default=2,
        help_text="Max AI responses before suggesting human handoff")
    handoff_triggers = models.JSONField(default=list,
        help_text="Keywords/phrases that trigger human handoff")

    # Statistics
    total_conversations = models.PositiveIntegerField(default=0)
    total_messages = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('AI Agent')
        verbose_name_plural = _('AI Agents')

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class Intent(models.Model):
    """Training intents for AI agents"""

    ai_agent = models.ForeignKey(AIAgent, on_delete=models.CASCADE, related_name='intents')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Training examples
    examples = models.JSONField(default=list, help_text="List of training examples")

    # Response templates
    responses = models.JSONField(default=list, help_text="List of possible responses")

    # Metadata
    confidence_threshold = models.FloatField(default=0.8)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Intent')
        verbose_name_plural = _('Intents')
        unique_together = ['ai_agent', 'name']

    def __str__(self):
        return f"{self.ai_agent.name} - {self.name}"


class Feedback(models.Model):
    """User feedback on conversations"""

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Rating and feedback
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)

    # Feedback categories
    categories = models.JSONField(default=list, help_text="Feedback categories (e.g., ['helpful', 'fast'])")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Feedback')
        verbose_name_plural = _('Feedbacks')
        unique_together = ['conversation', 'user']

    def __str__(self):
        return f"Feedback: {self.conversation.id} - {self.rating} stars"