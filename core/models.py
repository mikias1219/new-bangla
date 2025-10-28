from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Client(models.Model):
    """Client model for multi-business support"""
    
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    contact_email = models.EmailField()
    is_active = models.BooleanField(default=True)
    
    # Additional fields for better management
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='client_logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    
    # Settings
    max_conversations = models.PositiveIntegerField(default=1000)
    max_voice_minutes = models.PositiveIntegerField(default=100)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BanglaConversation(models.Model):
    """Simplified conversation model for BanglaChatPro requirements"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('escalated', 'Escalated to Human'),
        ('abandoned', 'Abandoned'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='conversations')
    user_name = models.CharField(max_length=100)
    user_message = models.TextField()
    ai_response = models.TextField()
    satisfaction_rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    is_escalated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Additional fields for better tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    escalated_at = models.DateTimeField(null=True, blank=True)
    human_response = models.TextField(blank=True)
    human_responded_at = models.DateTimeField(null=True, blank=True)
    
    # AI metadata
    ai_confidence = models.FloatField(null=True, blank=True)
    intent_detected = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Bangla Conversation')
        verbose_name_plural = _('Bangla Conversations')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Conversation {self.id} - {self.user_name}"


class CallLog(models.Model):
    """Call log model for voice feature"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    caller_name = models.CharField(max_length=100)
    question = models.TextField()
    ai_audio_response_url = models.URLField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True, help_text="Duration in seconds")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Additional fields for better tracking
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='call_logs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transcription = models.TextField(blank=True)
    ai_text_response = models.TextField(blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    language_detected = models.CharField(max_length=10, default='bn')
    
    # Error handling
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('Call Log')
        verbose_name_plural = _('Call Logs')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Call {self.id} - {self.caller_name}"


class BanglaIntent(models.Model):
    """Intent model for AI training"""
    
    name = models.CharField(max_length=100)
    training_phrase = models.TextField()
    ai_response_template = models.TextField()
    
    # Additional fields for better management
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='intents')
    description = models.TextField(blank=True)
    examples = models.JSONField(default=list, help_text="List of training examples")
    responses = models.JSONField(default=list, help_text="List of possible responses")
    
    # Settings
    confidence_threshold = models.FloatField(default=0.8)
    is_active = models.BooleanField(default=True)
    
    # Statistics
    usage_count = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Bangla Intent')
        verbose_name_plural = _('Bangla Intents')
        unique_together = ['client', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.client.name} - {self.name}"


class AdminProfile(models.Model):
    """Admin profile model"""
    
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='super_admin')
    
    # Additional fields
    avatar = models.ImageField(upload_to='admin_avatars/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Permissions
    can_manage_clients = models.BooleanField(default=True)
    can_manage_intents = models.BooleanField(default=True)
    can_view_analytics = models.BooleanField(default=True)
    can_handle_escalations = models.BooleanField(default=True)
    
    # Settings
    language = models.CharField(max_length=10, default='en', choices=[
        ('en', 'English'),
        ('bn', 'Bangla'),
    ])
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Activity tracking
    last_login = models.DateTimeField(null=True, blank=True)
    total_sessions = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Admin Profile')
        verbose_name_plural = _('Admin Profiles')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class SystemSettings(models.Model):
    """System settings model"""
    
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    data_type = models.CharField(max_length=20, choices=[
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ], default='string')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('System Setting')
        verbose_name_plural = _('System Settings')
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value}"
    
    def get_value(self):
        """Get the value with proper type conversion"""
        if self.data_type == 'integer':
            try:
                return int(self.value)
            except ValueError:
                return 0
        elif self.data_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.data_type == 'json':
            import json
            try:
                return json.loads(self.value)
            except json.JSONDecodeError:
                return {}
        return self.value


class Analytics(models.Model):
    """Analytics model for dashboard data"""
    
    PERIOD_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='analytics')
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='daily')
    date = models.DateField()
    
    # Chat metrics
    total_chats = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    failed_queries = models.PositiveIntegerField(default=0)
    escalated_chats = models.PositiveIntegerField(default=0)
    
    # Voice metrics
    total_calls = models.PositiveIntegerField(default=0)
    total_call_duration = models.PositiveIntegerField(default=0)  # in seconds
    
    # Satisfaction metrics
    average_rating = models.FloatField(default=0.0)
    total_ratings = models.PositiveIntegerField(default=0)
    
    # Response time metrics
    average_response_time = models.FloatField(default=0.0)  # in seconds
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Analytics')
        verbose_name_plural = _('Analytics')
        unique_together = ['client', 'period', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics {self.client.name} - {self.date}"
