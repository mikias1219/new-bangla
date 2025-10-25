from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Analytics(models.Model):
    """Analytics data for dashboard"""

    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE, related_name='analytics')

    # Time period
    date = models.DateField()
    period = models.CharField(max_length=20, choices=[
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='daily')

    # Conversation metrics
    total_conversations = models.PositiveIntegerField(default=0)
    active_conversations = models.PositiveIntegerField(default=0)
    completed_conversations = models.PositiveIntegerField(default=0)
    transferred_conversations = models.PositiveIntegerField(default=0)

    # Message metrics
    total_messages = models.PositiveIntegerField(default=0)
    ai_messages = models.PositiveIntegerField(default=0)
    human_messages = models.PositiveIntegerField(default=0)

    # User metrics
    unique_users = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    returning_users = models.PositiveIntegerField(default=0)

    # Performance metrics
    average_response_time = models.DurationField(null=True, blank=True)
    average_conversation_duration = models.DurationField(null=True, blank=True)
    satisfaction_score = models.FloatField(default=0.0)

    # Channel metrics
    web_conversations = models.PositiveIntegerField(default=0)
    voice_conversations = models.PositiveIntegerField(default=0)
    api_conversations = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Analytics')
        verbose_name_plural = _('Analytics')
        unique_together = ['organization', 'date', 'period']
        ordering = ['-date']

    def __str__(self):
        return f"{self.organization.name} - {self.date} ({self.period})"


class SystemSetting(models.Model):
    """System-wide settings"""

    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('security', 'Security'),
        ('api', 'API Integration'),
        ('voice', 'Voice'),
        ('chat', 'Chat'),
        ('handoff', 'Handoff'),
    ]

    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='settings', help_text="Null for global settings")

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    key = models.CharField(max_length=100)
    value = models.TextField()
    description = models.TextField(blank=True)

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('System Setting')
        verbose_name_plural = _('System Settings')
        unique_together = ['organization', 'category', 'key']

    def __str__(self):
        scope = self.organization.name if self.organization else "Global"
        return f"{scope} - {self.category}: {self.key}"


class LogEntry(models.Model):
    """System and user activity logs"""

    LEVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE,
                                     related_name='logs', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='logs')

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='info')
    category = models.CharField(max_length=50, choices=[
        ('auth', 'Authentication'),
        ('chat', 'Chat'),
        ('voice', 'Voice'),
        ('admin', 'Administration'),
        ('system', 'System'),
        ('security', 'Security'),
    ])

    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)

    # Request information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Log Entry')
        verbose_name_plural = _('Log Entries')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'level']),
            models.Index(fields=['organization', 'category']),
        ]

    def __str__(self):
        return f"{self.level.upper()}: {self.message[:50]}"


class Notification(models.Model):
    """User notifications"""

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='sent_notifications')

    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=[
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
        ('chat', 'Chat'),
        ('system', 'System'),
    ], default='info')

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Action URL
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username}: {self.title}"