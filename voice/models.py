from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

class VoiceRecording(models.Model):
    """Voice recording for processing"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voice_recordings')
    conversation = models.ForeignKey('chat.Conversation', on_delete=models.CASCADE, related_name='voice_recordings')

    # File information
    audio_file = models.FileField(upload_to='voice_recordings/')
    file_format = models.CharField(max_length=10, choices=[
        ('wav', 'WAV'),
        ('mp3', 'MP3'),
        ('ogg', 'OGG'),
        ('webm', 'WebM'),
        ('m4a', 'M4A'),
    ])

    # Metadata
    duration = models.DurationField(null=True, blank=True)  # Duration in seconds
    file_size = models.PositiveIntegerField()  # Size in bytes
    sample_rate = models.PositiveIntegerField(null=True, blank=True)  # Hz

    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)

    # Transcription
    transcription = models.TextField(blank=True)
    confidence_score = models.FloatField(null=True, blank=True)

    # Language detection
    detected_language = models.CharField(max_length=10, blank=True)
    language_confidence = models.FloatField(null=True, blank=True)

    # Error information
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Voice Recording')
        verbose_name_plural = _('Voice Recordings')
        ordering = ['-created_at']

    def __str__(self):
        return f"Voice Recording {self.id} - {self.user.username}"


class VoiceSession(models.Model):
    """Voice chat session"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('interrupted', 'Interrupted'),
        ('failed', 'Failed'),
    ]

    conversation = models.OneToOneField('chat.Conversation', on_delete=models.CASCADE, related_name='voice_session')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voice_sessions')

    # Session information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    session_id = models.CharField(max_length=255, unique=True)

    # Voice settings
    voice_type = models.CharField(max_length=50, default='neutral', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('neutral', 'Neutral'),
        ('young', 'Young'),
        ('old', 'Old'),
    ])

    language = models.CharField(max_length=10, default='en')
    speed = models.FloatField(default=1.0)  # 0.5 - 2.0

    # Statistics
    total_recordings = models.PositiveIntegerField(default=0)
    total_duration = models.DurationField(default=timedelta())
    average_confidence = models.FloatField(default=0.0)

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Voice Session')
        verbose_name_plural = _('Voice Sessions')
        ordering = ['-started_at']

    def __str__(self):
        return f"Voice Session {self.session_id} - {self.user.username}"


class SpeechSynthesis(models.Model):
    """Text-to-speech synthesis records"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    message = models.OneToOneField('chat.Message', on_delete=models.CASCADE, related_name='speech_synthesis')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='speech_syntheses')

    # Synthesis settings
    voice_type = models.CharField(max_length=50, default='neutral')
    language = models.CharField(max_length=10, default='en')
    speed = models.FloatField(default=1.0)

    # Output
    audio_file = models.FileField(upload_to='synthesized_speech/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Processing info
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    # Error information
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Speech Synthesis')
        verbose_name_plural = _('Speech Syntheses')
        ordering = ['-created_at']

    def __str__(self):
        return f"TTS for Message {self.message.id}"


class VoiceAnalytics(models.Model):
    """Voice-specific analytics"""

    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE, related_name='voice_analytics')

    # Time period
    date = models.DateField()
    period = models.CharField(max_length=20, choices=[
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='daily')

    # Voice metrics
    total_voice_sessions = models.PositiveIntegerField(default=0)
    total_recordings = models.PositiveIntegerField(default=0)
    total_speech_syntheses = models.PositiveIntegerField(default=0)

    # Quality metrics
    average_transcription_confidence = models.FloatField(default=0.0)
    average_language_detection_confidence = models.FloatField(default=0.0)

    # Usage metrics
    total_audio_duration = models.DurationField(default=timedelta())  # Total duration of all recordings
    average_session_duration = models.DurationField(null=True, blank=True)

    # Error metrics
    failed_transcriptions = models.PositiveIntegerField(default=0)
    failed_syntheses = models.PositiveIntegerField(default=0)

    # Language distribution
    language_distribution = models.JSONField(default=dict)

    class Meta:
        verbose_name = _('Voice Analytics')
        verbose_name_plural = _('Voice Analytics')
        unique_together = ['organization', 'date', 'period']
        ordering = ['-date']

    def __str__(self):
        return f"Voice Analytics {self.organization.name} - {self.date}"