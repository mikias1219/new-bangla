from django.contrib import admin
from .models import (
    Client, BanglaConversation, CallLog, BanglaIntent, 
    AdminProfile, SystemSettings, Analytics
)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'contact_email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'domain', 'contact_email']
    list_editable = ['is_active']
    ordering = ['name']


@admin.register(BanglaConversation)
class BanglaConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'user_name', 'status', 'is_escalated', 'satisfaction_rating', 'created_at']
    list_filter = ['status', 'is_escalated', 'client', 'created_at']
    search_fields = ['user_name', 'user_message', 'ai_response']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'caller_name', 'status', 'duration', 'timestamp']
    list_filter = ['status', 'client', 'timestamp']
    search_fields = ['caller_name', 'question', 'transcription']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']


@admin.register(BanglaIntent)
class BanglaIntentAdmin(admin.ModelAdmin):
    list_display = ['name', 'client', 'is_active', 'usage_count', 'success_rate', 'created_at']
    list_filter = ['is_active', 'client', 'created_at']
    search_fields = ['name', 'training_phrase', 'ai_response_template']
    list_editable = ['is_active']
    ordering = ['name']


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'can_manage_clients', 'can_manage_intents', 'last_login']
    list_filter = ['role', 'can_manage_clients', 'can_manage_intents']
    search_fields = ['user__username', 'user__email', 'department']
    ordering = ['user__username']


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'data_type', 'updated_at']
    list_filter = ['data_type', 'updated_at']
    search_fields = ['key', 'description']
    ordering = ['key']


@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ['client', 'period', 'date', 'total_chats', 'active_users', 'average_rating']
    list_filter = ['period', 'client', 'date']
    search_fields = ['client__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date']
