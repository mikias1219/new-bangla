from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AdminActivity(models.Model):
    """Admin activity log"""

    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create_org', 'Create Organization'),
        ('update_org', 'Update Organization'),
        ('delete_org', 'Delete Organization'),
        ('create_user', 'Create User'),
        ('update_user', 'Update User'),
        ('delete_user', 'Delete User'),
        ('subscription_change', 'Subscription Change'),
        ('payment_processed', 'Payment Processed'),
        ('api_key_created', 'API Key Created'),
        ('api_key_revoked', 'API Key Revoked'),
        ('system_config', 'System Configuration'),
    ]

    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    target_object = models.CharField(max_length=100, blank=True, help_text="Model name of affected object")
    target_id = models.PositiveIntegerField(null=True, blank=True, help_text="ID of affected object")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Admin Activity')
        verbose_name_plural = _('Admin Activities')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.admin_user.username} - {self.activity_type} - {self.created_at}"


class SystemSettings(models.Model):
    """Global system settings"""

    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    value_type = models.CharField(max_length=20, choices=[
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ], default='string')
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False, help_text="Can be accessed via API")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('System Setting')
        verbose_name_plural = _('System Settings')

    def __str__(self):
        return f"{self.key}: {self.value}"


class ClientSupportTicket(models.Model):
    """Support tickets from clients"""

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_client', 'Waiting for Client'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE, related_name='support_tickets')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tickets')

    # Ticket details
    subject = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')

    # Assignment
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='assigned_tickets')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    tags = models.JSONField(default=list)
    attachments = models.JSONField(default=list)

    class Meta:
        verbose_name = _('Client Support Ticket')
        verbose_name_plural = _('Client Support Tickets')
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"


class SupportMessage(models.Model):
    """Messages within support tickets"""

    ticket = models.ForeignKey(ClientSupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_internal = models.BooleanField(default=False, help_text="Internal note visible only to support staff")
    attachments = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Support Message')
        verbose_name_plural = _('Support Messages')
        ordering = ['created_at']

    def __str__(self):
        return f"Message in Ticket #{self.ticket.id}"


class UsageAnalytics(models.Model):
    """System-wide usage analytics"""

    # Time period
    date = models.DateField()
    period = models.CharField(max_length=20, choices=[
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='daily')

    # Organization metrics
    total_organizations = models.PositiveIntegerField(default=0)
    active_organizations = models.PositiveIntegerField(default=0)
    trial_organizations = models.PositiveIntegerField(default=0)

    # User metrics
    total_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)

    # Conversation metrics
    total_conversations = models.PositiveIntegerField(default=0)
    active_conversations = models.PositiveIntegerField(default=0)
    ai_responses = models.PositiveIntegerField(default=0)

    # Voice metrics
    total_voice_minutes = models.PositiveIntegerField(default=0)
    voice_sessions = models.PositiveIntegerField(default=0)

    # Payment metrics
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_subscriptions = models.PositiveIntegerField(default=0)
    cancelled_subscriptions = models.PositiveIntegerField(default=0)

    # Social media metrics
    social_messages_received = models.PositiveIntegerField(default=0)
    social_messages_sent = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Usage Analytics')
        verbose_name_plural = _('Usage Analytics')
        unique_together = ['date', 'period']
        ordering = ['-date']

    def __str__(self):
        return f"Analytics {self.date} ({self.period})"


class Notification(models.Model):
    """System notifications for admins and clients"""

    RECIPIENT_TYPES = [
        ('admin', 'Admin Users'),
        ('client', 'Client Organizations'),
        ('specific_user', 'Specific User'),
        ('all', 'All Users'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=255)
    message = models.TextField()
    recipient_type = models.CharField(max_length=15, choices=RECIPIENT_TYPES, default='admin')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    # Recipients
    recipient_organizations = models.ManyToManyField('accounts.Organization', blank=True,
                                                    related_name='admin_notifications')
    recipient_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                            related_name='admin_notifications')

    # Timing
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Status
    is_sent = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    # Metadata
    action_url = models.URLField(blank=True, help_text="URL to redirect when clicked")
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification: {self.title}"


class DataExport(models.Model):
    """Data export requests"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    EXPORT_TYPES = [
        ('organization_data', 'Organization Data'),
        ('conversation_history', 'Conversation History'),
        ('analytics', 'Analytics Data'),
        ('payment_history', 'Payment History'),
        ('system_logs', 'System Logs'),
    ]

    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    export_type = models.CharField(max_length=20, choices=EXPORT_TYPES)
    organization = models.ForeignKey('accounts.Organization', on_delete=models.SET_NULL,
                                    null=True, blank=True)

    # Export parameters
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    filters = models.JSONField(default=dict)

    # Status
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    file_url = models.URLField(blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)  # Size in bytes
    error_message = models.TextField(blank=True)

    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Data Export')
        verbose_name_plural = _('Data Exports')
        ordering = ['-requested_at']

    def __str__(self):
        return f"Export {self.export_type} - {self.requested_by.username}"