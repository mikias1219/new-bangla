from django.contrib import admin
from .models import VoiceRecording, VoiceSession, SpeechSynthesis, VoiceAnalytics

@admin.register(VoiceRecording)
class VoiceRecordingAdmin(admin.ModelAdmin):
    """Voice Recording admin"""
    list_display = ('id', 'user', 'conversation', 'status', 'duration', 'confidence_score', 'created_at')
    list_filter = ('status', 'file_format', 'detected_language', 'created_at')
    search_fields = ('user__username', 'transcription')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(VoiceSession)
class VoiceSessionAdmin(admin.ModelAdmin):
    """Voice Session admin"""
    list_display = ('session_id', 'user', 'status', 'voice_type', 'language', 'total_recordings', 'started_at')
    list_filter = ('status', 'voice_type', 'language')
    search_fields = ('session_id', 'user__username')
    readonly_fields = ('session_id', 'started_at', 'last_activity', 'ended_at')
    ordering = ('-started_at',)

@admin.register(SpeechSynthesis)
class SpeechSynthesisAdmin(admin.ModelAdmin):
    """Speech Synthesis admin"""
    list_display = ('id', 'user', 'message', 'status', 'voice_type', 'created_at')
    list_filter = ('status', 'voice_type', 'language')
    search_fields = ('user__username', 'message__content')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(VoiceAnalytics)
class VoiceAnalyticsAdmin(admin.ModelAdmin):
    """Voice Analytics admin"""
    list_display = ('organization', 'date', 'period', 'total_voice_sessions', 'total_recordings', 'average_transcription_confidence')
    list_filter = ('period', 'organization', 'date')
    search_fields = ('organization__name',)
    readonly_fields = ('date', 'period')
    ordering = ('-date',)