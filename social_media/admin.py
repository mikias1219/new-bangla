from django.contrib import admin
from .models import (
    SocialMediaAccount, SocialMediaMessage, SocialMediaAutoReply, 
    SocialMediaWebhook, SocialMediaAnalytics
)


@admin.register(SocialMediaAccount)
class SocialMediaAccountAdmin(admin.ModelAdmin):
    list_display = ['platform', 'account_name', 'organization', 'is_active', 'connected_at']
    list_filter = ['platform', 'is_active', 'connected_at']
    search_fields = ['account_name', 'organization__name', 'platform']
    readonly_fields = ['connected_at', 'last_sync_at']
    ordering = ['-connected_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('platform', 'account_name', 'organization', 'is_active')
        }),
        ('Credentials', {
            'fields': ('access_token', 'refresh_token', 'token_expires_at'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('webhook_url', 'auto_reply_enabled', 'response_delay')
        }),
        ('Timestamps', {
            'fields': ('connected_at', 'last_sync_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SocialMediaMessage)
class SocialMediaMessageAdmin(admin.ModelAdmin):
    list_display = ['social_account', 'sender_id', 'message_type', 'is_ai_response', 'received_at']
    list_filter = ['message_type', 'is_ai_response', 'received_at', 'social_account__platform']
    search_fields = ['content', 'sender_id', 'social_account__account_name']
    readonly_fields = ['received_at', 'sent_at']
    ordering = ['-received_at']
    
    fieldsets = (
        ('Message Information', {
            'fields': ('social_account', 'sender_id', 'message_type', 'content')
        }),
        ('Response Details', {
            'fields': ('is_ai_response', 'ai_agent', 'response_time')
        }),
        ('Timestamps', {
            'fields': ('received_at', 'sent_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SocialMediaAutoReply)
class SocialMediaAutoReplyAdmin(admin.ModelAdmin):
    list_display = ['social_account', 'trigger_type', 'priority', 'is_active', 'created_at']
    list_filter = ['trigger_type', 'is_active', 'priority', 'created_at']
    search_fields = ['trigger_keywords', 'response_text', 'social_account__account_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Auto-Reply Configuration', {
            'fields': ('social_account', 'trigger_type', 'trigger_keywords', 'priority', 'is_active')
        }),
        ('Response Content', {
            'fields': ('response_text', 'response_template')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SocialMediaWebhook)
class SocialMediaWebhookAdmin(admin.ModelAdmin):
    list_display = ['platform', 'organization', 'is_active', 'created_at']
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['webhook_url', 'organization__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Webhook Configuration', {
            'fields': ('platform', 'organization', 'webhook_url', 'is_active')
        }),
        ('Security', {
            'fields': ('secret_key', 'verify_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SocialMediaAnalytics)
class SocialMediaAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['social_account', 'date', 'messages_received', 'messages_sent', 'ai_responses']
    list_filter = ['date', 'social_account__platform']
    search_fields = ['social_account__account_name', 'social_account__organization__name']
    readonly_fields = ['created_at']
    ordering = ['-date']
    
    fieldsets = (
        ('Analytics Data', {
            'fields': ('social_account', 'date', 'messages_received', 'messages_sent', 'ai_responses')
        }),
        ('Performance Metrics', {
            'fields': ('avg_response_time', 'satisfaction_score', 'engagement_rate')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
