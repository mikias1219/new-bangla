from django.db import models
from django.contrib.auth.models import User
from accounts.models import Organization
from django.utils import timezone


class ClientOnboardingStep(models.Model):
    """Track client onboarding progress"""
    STEP_CHOICES = [
        ('welcome', 'Welcome & Setup'),
        ('organization', 'Organization Setup'),
        ('api_keys', 'API Keys Configuration'),
        ('social_media', 'Social Media Integration'),
        ('voice_setup', 'Voice Call Setup'),
        ('ai_agent', 'AI Agent Configuration'),
        ('testing', 'Testing & Validation'),
        ('completed', 'Onboarding Completed'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='onboarding_steps')
    step_name = models.CharField(max_length=50, choices=STEP_CHOICES)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['organization', 'step_name']
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.organization.name} - {self.get_step_name_display()}"
    
    def complete_step(self):
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()


class ClientSetupGuide(models.Model):
    """Setup guides for different services"""
    SERVICE_CHOICES = [
        ('openai', 'OpenAI API'),
        ('twilio', 'Twilio'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp Business'),
        ('twitter', 'Twitter'),
    ]
    
    service_name = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    setup_instructions = models.TextField()
    api_documentation_url = models.URLField(blank=True)
    video_tutorial_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['service_name']
    
    def __str__(self):
        return f"{self.get_service_name_display()} - {self.title}"


class ClientSupportTicket(models.Model):
    """Support tickets for client onboarding"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='support_tickets')
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.organization.name}"


class ClientFeedback(models.Model):
    """Client feedback during onboarding"""
    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='feedback')
    step_name = models.CharField(max_length=50)
    rating = models.IntegerField(choices=RATING_CHOICES)
    feedback_text = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.organization.name} - {self.step_name} ({self.rating}/5)"