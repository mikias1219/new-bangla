from django.contrib import admin
from .models import ClientOnboardingStep, ClientSetupGuide, ClientSupportTicket, ClientFeedback


@admin.register(ClientOnboardingStep)
class ClientOnboardingStepAdmin(admin.ModelAdmin):
    list_display = ['organization', 'step_name', 'is_completed', 'completed_at', 'created_at']
    list_filter = ['step_name', 'is_completed', 'created_at']
    search_fields = ['organization__name', 'step_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'step_name', 'is_completed', 'completed_at')
        }),
        ('Details', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClientSetupGuide)
class ClientSetupGuideAdmin(admin.ModelAdmin):
    list_display = ['service_name', 'title', 'is_active', 'created_at']
    list_filter = ['service_name', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'service_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['service_name', 'title']
    
    fieldsets = (
        ('Service Information', {
            'fields': ('service_name', 'title', 'description', 'is_active')
        }),
        ('Setup Instructions', {
            'fields': ('setup_instructions',)
        }),
        ('Resources', {
            'fields': ('api_documentation_url', 'video_tutorial_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClientSupportTicket)
class ClientSupportTicketAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'priority', 'status', 'created_by', 'assigned_to', 'created_at']
    list_filter = ['priority', 'status', 'created_at', 'assigned_to']
    search_fields = ['title', 'description', 'organization__name', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('title', 'description', 'organization', 'priority', 'status')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Resolution', {
            'fields': ('resolved_at',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new ticket
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ClientFeedback)
class ClientFeedbackAdmin(admin.ModelAdmin):
    list_display = ['organization', 'step_name', 'rating', 'created_at']
    list_filter = ['step_name', 'rating', 'created_at']
    search_fields = ['organization__name', 'step_name', 'feedback_text']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('organization', 'step_name', 'rating')
        }),
        ('Content', {
            'fields': ('feedback_text', 'suggestions')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
