from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class SocialMediaAccount(models.Model):
    """Social media account connection"""

    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('linkedin', 'LinkedIn'),
        ('messenger', 'Facebook Messenger'),
    ]

    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE, related_name='social_accounts')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)

    # Account details
    account_name = models.CharField(max_length=100)
    account_id = models.CharField(max_length=255, help_text="Platform-specific account ID")
    display_name = models.CharField(max_length=255, blank=True)
    profile_url = models.URLField(blank=True)

    # Authentication
    access_token = models.TextField(blank=True, help_text="OAuth access token")
    refresh_token = models.TextField(blank=True, help_text="OAuth refresh token")
    token_expires_at = models.DateTimeField(null=True, blank=True)

    # Webhook configuration
    webhook_url = models.URLField(blank=True, help_text="Webhook URL for receiving messages")
    webhook_secret = models.CharField(max_length=255, blank=True, help_text="Webhook verification secret")

    # Settings
    is_active = models.BooleanField(default=True)
    auto_reply_enabled = models.BooleanField(default=True)
    business_hours_only = models.BooleanField(default=False)
    business_hours_start = models.TimeField(null=True, blank=True)
    business_hours_end = models.TimeField(null=True, blank=True)

    # Assigned AI agent
    ai_agent = models.ForeignKey('chat.AIAgent', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='social_accounts')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Social Media Account')
        verbose_name_plural = _('Social Media Accounts')
        unique_together = ['organization', 'platform', 'account_id']

    def __str__(self):
        return f"{self.organization.name} - {self.platform} - {self.account_name}"

class SocialMediaMessage(models.Model):
    """Messages from social media platforms"""

    MESSAGE_TYPE_CHOICES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('system', 'System'),
    ]

    social_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, related_name='messages')
    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE, related_name='social_messages')

    # Message details
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='incoming')
    platform_message_id = models.CharField(max_length=255, help_text="Platform-specific message ID")
    sender_id = models.CharField(max_length=255, help_text="Sender's platform ID")
    sender_name = models.CharField(max_length=255, blank=True)

    # Conversation tracking
    conversation = models.ForeignKey('chat.Conversation', on_delete=models.CASCADE, related_name='social_messages')
    thread_id = models.CharField(max_length=255, blank=True, help_text="Platform thread/conversation ID")

    # Message content
    content = models.TextField()
    content_type = models.CharField(max_length=20, default='text', choices=[
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('file', 'File'),
        ('location', 'Location'),
    ])

    # Attachments
    attachments = models.JSONField(default=list, help_text="List of attachment URLs/metadata")

    # AI processing
    ai_processed = models.BooleanField(default=False)
    ai_response = models.TextField(blank=True)
    ai_confidence = models.FloatField(null=True, blank=True)

    # Status
    is_read = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Social Media Message')
        verbose_name_plural = _('Social Media Messages')
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['social_account', 'thread_id']),
            models.Index(fields=['platform_message_id']),
        ]

    def __str__(self):
        return f"{self.social_account.platform} - {self.sender_name}: {self.content[:50]}"


class SocialMediaWebhook(models.Model):
    """Webhook events from social media platforms"""

    social_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, related_name='webhooks')

    # Webhook data
    event_type = models.CharField(max_length=100)
    event_id = models.CharField(max_length=255, unique=True)
    raw_payload = models.JSONField()

    # Processing
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Social Media Webhook')
        verbose_name_plural = _('Social Media Webhooks')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.social_account.platform} - {self.event_type}"


class SocialMediaAnalytics(models.Model):
    """Analytics for social media integrations"""

    social_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, related_name='analytics')

    # Time period
    date = models.DateField()
    period = models.CharField(max_length=20, choices=[
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='daily')

    # Message metrics
    messages_received = models.PositiveIntegerField(default=0)
    messages_sent = models.PositiveIntegerField(default=0)
    ai_responses = models.PositiveIntegerField(default=0)

    # Response metrics
    average_response_time = models.DurationField(null=True, blank=True)
    response_rate = models.FloatField(default=0.0)  # Percentage
    customer_satisfaction = models.FloatField(null=True, blank=True)  # 1-5 scale

    # Content metrics
    messages_with_attachments = models.PositiveIntegerField(default=0)
    popular_content_types = models.JSONField(default=dict)

    # Error metrics
    failed_webhooks = models.PositiveIntegerField(default=0)
    failed_responses = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Social Media Analytics')
        verbose_name_plural = _('Social Media Analytics')
        unique_together = ['social_account', 'date', 'period']
        ordering = ['-date']

    def __str__(self):
        return f"Analytics {self.social_account.account_name} - {self.date}"


class SocialMediaAutoReply(models.Model):
    """Automated replies for social media"""

    social_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, related_name='auto_replies')

    # Trigger conditions
    trigger_keywords = models.JSONField(default=list, help_text="Keywords that trigger this reply")
    trigger_type = models.CharField(max_length=20, choices=[
        ('keyword', 'Keyword Match'),
        ('exact', 'Exact Match'),
        ('contains', 'Contains Text'),
        ('regex', 'Regular Expression'),
    ], default='keyword')

    # Response
    response_text = models.TextField()
    response_type = models.CharField(max_length=20, choices=[
        ('text', 'Text Only'),
        ('with_buttons', 'Text with Buttons'),
        ('quick_replies', 'Quick Replies'),
        ('template', 'Template Message'),
    ], default='text')

    # Advanced options
    response_buttons = models.JSONField(default=list, help_text="Button configurations")
    response_attachments = models.JSONField(default=list, help_text="Attachment URLs")

    # Conditions
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0, help_text="Higher priority replies are checked first")
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Max times this reply can be used")
    usage_count = models.PositiveIntegerField(default=0)

    # Timing
    delay_seconds = models.PositiveIntegerField(default=0, help_text="Delay before sending reply")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Social Media Auto Reply')
        verbose_name_plural = _('Social Media Auto Replies')
        ordering = ['-priority', 'created_at']

    def __str__(self):
        return f"Auto Reply: {self.trigger_keywords[:50]}..."