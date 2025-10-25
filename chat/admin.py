from django.contrib import admin
from .models import Conversation, Message, AIAgent, Intent, Feedback

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Conversation admin"""
    list_display = ('id', 'user', 'organization', 'status', 'ai_agent', 'message_count', 'started_at', 'last_message_at')
    list_filter = ('status', 'organization', 'ai_agent', 'started_at')
    search_fields = ('user__username', 'user__email', 'title')
    readonly_fields = ('id', 'started_at', 'last_message_at', 'message_count')
    ordering = ('-last_message_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'organization', 'ai_agent', 'status', 'title')
        }),
        ('Transfer Information', {
            'fields': ('transferred_to', 'transfer_reason'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('message_count', 'ai_responses', 'started_at', 'last_message_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Message admin"""
    list_display = ('id', 'conversation', 'sender_type', 'sender', 'timestamp', 'content_preview')
    list_filter = ('sender_type', 'content_type', 'timestamp')
    search_fields = ('content', 'sender__username')
    readonly_fields = ('id', 'timestamp')
    ordering = ('-timestamp',)

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(AIAgent)
class AIAgentAdmin(admin.ModelAdmin):
    """AI Agent admin"""
    list_display = ('name', 'organization', 'status', 'model_provider', 'model_name', 'total_conversations', 'average_rating', 'created_at')
    list_filter = ('status', 'model_provider', 'organization', 'supported_languages')
    search_fields = ('name', 'description')
    readonly_fields = ('total_conversations', 'total_messages', 'average_rating', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'name', 'description', 'avatar')
        }),
        ('Configuration', {
            'fields': ('status', 'model_provider', 'model_name', 'system_prompt', 'temperature', 'max_tokens')
        }),
        ('Language Support', {
            'fields': ('supported_languages', 'primary_language')
        }),
        ('Capabilities', {
            'fields': ('voice_enabled', 'file_processing')
        }),
        ('Handoff Settings', {
            'fields': ('max_consecutive_responses', 'handoff_triggers')
        }),
        ('Statistics', {
            'fields': ('total_conversations', 'total_messages', 'average_rating'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Intent)
class IntentAdmin(admin.ModelAdmin):
    """Intent admin"""
    list_display = ('name', 'ai_agent', 'confidence_threshold', 'is_active', 'created_at')
    list_filter = ('is_active', 'ai_agent', 'confidence_threshold')
    search_fields = ('name', 'description')
    ordering = ('ai_agent', 'name')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Feedback admin"""
    list_display = ('conversation', 'user', 'rating', 'comment_preview', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'comment', 'conversation__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment'