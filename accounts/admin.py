from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Organization, APIKey

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom user admin"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'organization', 'is_admin', 'is_active')
    list_filter = ('organization', 'is_admin', 'is_active', 'language')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone', 'organization', 'avatar', 'language', 'is_admin')
        }),
    )

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Organization admin"""
    list_display = ('name', 'subscription_plan', 'is_active', 'max_users', 'created_at')
    list_filter = ('subscription_plan', 'is_active')
    search_fields = ('name', 'contact_email')
    ordering = ('name',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'website', 'logo')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Subscription', {
            'fields': ('subscription_plan', 'subscription_start', 'subscription_end', 'is_active')
        }),
        ('Limits', {
            'fields': ('max_users', 'max_conversations')
        }),
    )

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """API Key admin"""
    list_display = ('organization', 'name', 'provider', 'is_active', 'last_used', 'created_at')
    list_filter = ('provider', 'is_active', 'organization')
    search_fields = ('name', 'key')
    readonly_fields = ('key', 'last_used', 'created_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'name', 'provider')
        }),
        ('Configuration', {
            'fields': ('key', 'is_active')
        }),
        ('Usage', {
            'fields': ('last_used', 'created_at'),
            'classes': ('collapse',)
        }),
    )