from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom user model for BanglaChatPro"""

    # Additional fields
    phone = models.CharField(max_length=15, blank=True, help_text="Phone number")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    organization = models.ForeignKey('Organization', on_delete=models.SET_NULL, null=True, blank=True)
    is_admin = models.BooleanField(default=False, help_text="Is this user an admin?")

    # Preferences
    language = models.CharField(max_length=10, default='en', choices=[
        ('en', 'English'),
        ('bn', 'Bangla'),
    ])

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f"{self.username} ({self.get_full_name() or self.email})"


class Organization(models.Model):
    """Organization model for multi-tenancy"""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='organization_logos/', blank=True, null=True)

    # Subscription details
    subscription_plan = models.CharField(max_length=50, choices=[
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ], default='free')

    subscription_start = models.DateTimeField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Contact information
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)

    # Settings
    max_users = models.PositiveIntegerField(default=10)
    max_conversations = models.PositiveIntegerField(default=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')

    def __str__(self):
        return self.name


class APIKey(models.Model):
    """API Keys for external integrations"""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=255, unique=True)
    provider = models.CharField(max_length=50, choices=[
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('google', 'Google AI'),
        ('azure', 'Azure OpenAI'),
        ('custom', 'Custom'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('API Key')
        verbose_name_plural = _('API Keys')

    def __str__(self):
        return f"{self.organization.name} - {self.name}"