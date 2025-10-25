from django.contrib import admin
from .models import Analytics, SystemSetting, LogEntry, Notification

@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    """Analytics admin"""
    list_display = ('organization', 'date', 'period', 'total_conversations', 'total_messages', 'unique_users')
    list_filter = ('period', 'organization', 'date')
    search_fields = ('organization__name',)
    readonly_fields = ('date', 'period')
    ordering = ('-date',)

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    """System Setting admin"""
    list_display = ('get_scope', 'category', 'key', 'value_preview', 'is_active', 'updated_at')
    list_filter = ('category', 'is_active', 'organization')
    search_fields = ('key', 'value', 'description')
    ordering = ('category', 'key')

    def get_scope(self, obj):
        return obj.organization.name if obj.organization else "Global"
    get_scope.short_description = 'Scope'

    def value_preview(self, obj):
        return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Value'

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """Log Entry admin"""
    list_display = ('level', 'category', 'message_preview', 'user', 'organization', 'timestamp')
    list_filter = ('level', 'category', 'organization', 'timestamp')
    search_fields = ('message', 'user__username', 'ip_address')
    readonly_fields = ('timestamp', 'id')
    ordering = ('-timestamp',)

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin"""
    list_display = ('recipient', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)