from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from accounts.models import Organization, User, APIKey, Subscription, Payment
from chat.models import Conversation, Message, AIAgent
from voice.models import VoiceSession, VoiceRecording
from social_media.models import SocialMediaAccount, SocialMediaMessage
from client_onboarding.models import ClientOnboardingStep, ClientSupportTicket


class BanglaChatProAdminSite(AdminSite):
    """Custom admin site for BanglaChatPro"""
    site_header = "BanglaChatPro Administration"
    site_title = "BanglaChatPro Admin"
    index_title = "Welcome to BanglaChatPro Administration"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('analytics/', self.admin_view(self.analytics_view), name='analytics'),
            path('client-management/', self.admin_view(self.client_management_view), name='client_management'),
            path('system-health/', self.admin_view(self.system_health_view), name='system_health'),
            path('super-admin/', self.admin_view(self.super_admin_dashboard), name='super_admin'),
            path('api/approve-organization/<int:org_id>/', self.admin_view(self.approve_organization_api), name='approve_organization'),
            path('api/reject-organization/<int:org_id>/', self.admin_view(self.reject_organization_api), name='reject_organization'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        """Main dashboard view"""
        context = {
            'title': 'Dashboard Overview',
            'total_organizations': Organization.objects.count(),
            'total_users': User.objects.count(),
            'total_conversations': Conversation.objects.count(),
            'total_messages': Message.objects.count(),
            'active_ai_agents': AIAgent.objects.filter(status='active').count(),
            'recent_conversations': Conversation.objects.order_by('-last_message_at')[:10],
            'recent_support_tickets': ClientSupportTicket.objects.order_by('-created_at')[:5],
        }
        return render(request, 'admin/dashboard.html', context)

    def analytics_view(self, request):
        """Analytics view"""
        # Get analytics data for the last 30 days
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        context = {
            'title': 'Analytics Overview',
            'conversations_by_day': Conversation.objects.filter(
                started_at__gte=start_date
            ).extra(select={'day': 'date(started_at)'}).values('day').annotate(count=Count('id')),
            'messages_by_type': Message.objects.values('sender_type').annotate(count=Count('id')),
            'ai_agent_performance': AIAgent.objects.annotate(
                conversation_count=Count('conversations'),
                avg_rating=Avg('conversations__feedback__rating')
            ),
            'voice_sessions': VoiceSession.objects.filter(started_at__gte=start_date).count(),
            'social_messages': SocialMediaMessage.objects.filter(received_at__gte=start_date).count(),
        }
        return render(request, 'admin/analytics.html', context)

    def client_management_view(self, request):
        """Client management view"""
        context = {
            'title': 'Client Management',
            'organizations': Organization.objects.annotate(
                user_count=Count('users'),
                conversation_count=Count('conversations'),
                onboarding_progress=Count('onboarding_steps', filter=Q(onboarding_steps__is_completed=True))
            ),
            'pending_onboarding': ClientOnboardingStep.objects.filter(is_completed=False),
            'support_tickets': ClientSupportTicket.objects.filter(status='open'),
        }
        return render(request, 'admin/client_management.html', context)

    def system_health_view(self, request):
        """System health view"""
        context = {
            'title': 'System Health',
            'api_keys': APIKey.objects.filter(is_active=True),
            'ai_agents': AIAgent.objects.filter(status='active'),
            'social_accounts': SocialMediaAccount.objects.filter(is_active=True),
            'recent_errors': [],  # You can add error logging here
            'system_stats': {
                'database_size': 'N/A',  # You can add database size calculation
                'memory_usage': 'N/A',   # You can add memory usage
                'disk_usage': 'N/A',     # You can add disk usage
            }
        }
        return render(request, 'admin/system_health.html', context)

    def super_admin_dashboard(self, request):
        """Super admin dashboard view"""
        # Get statistics
        total_organizations = Organization.objects.count()
        pending_approvals = Organization.objects.filter(approval_status='pending').count()
        total_users = User.objects.count()
        total_conversations = Conversation.objects.count()
        
        # Get pending organizations
        pending_organizations = Organization.objects.filter(approval_status='pending').order_by('-created_at')[:10]
        
        # Get recent activities (you can expand this)
        recent_activities = []
        
        context = {
            'title': 'Super Admin Dashboard',
            'total_organizations': total_organizations,
            'pending_approvals': pending_approvals,
            'total_users': total_users,
            'total_conversations': total_conversations,
            'pending_organizations': pending_organizations,
            'recent_activities': recent_activities,
        }
        
        return render(request, 'admin/super_admin_dashboard.html', context)

    @method_decorator(csrf_exempt)
    def approve_organization_api(self, request, org_id):
        """API endpoint to approve organization"""
        try:
            organization = Organization.objects.get(id=org_id)
            organization.approval_status = 'approved'
            organization.approved_by = request.user
            organization.approved_at = timezone.now()
            organization.is_active = True
            organization.save()
            
            return JsonResponse({'success': True, 'message': 'Organization approved successfully'})
        except Organization.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Organization not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    @method_decorator(csrf_exempt)
    def reject_organization_api(self, request, org_id):
        """API endpoint to reject organization"""
        try:
            data = json.loads(request.body)
            reason = data.get('reason', '')
            
            organization = Organization.objects.get(id=org_id)
            organization.approval_status = 'rejected'
            organization.approved_by = request.user
            organization.approved_at = timezone.now()
            organization.rejection_reason = reason
            organization.is_active = False
            organization.save()
            
            return JsonResponse({'success': True, 'message': 'Organization rejected successfully'})
        except Organization.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Organization not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def index(self, request, extra_context=None):
        """Custom index page"""
        extra_context = extra_context or {}
        extra_context.update({
            'dashboard_url': reverse('admin:dashboard'),
            'analytics_url': reverse('admin:analytics'),
            'client_management_url': reverse('admin:client_management'),
            'system_health_url': reverse('admin:system_health'),
            'super_admin_url': reverse('admin:super_admin'),
        })
        return super().index(request, extra_context)


# Create custom admin site instance
admin_site = BanglaChatProAdminSite(name='banglachatpro_admin')

# Register models with custom admin site
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

# Register User model
admin_site.register(User, UserAdmin)

# Register Organization model
@admin.register(Organization, site=admin_site)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'user_count', 'conversation_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Users'
    
    def conversation_count(self, obj):
        return obj.conversations.count()
    conversation_count.short_description = 'Conversations'

# Register APIKey model
@admin.register(APIKey, site=admin_site)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['organization', 'provider', 'is_active', 'created_at']
    list_filter = ['provider', 'is_active', 'created_at']
    search_fields = ['organization__name', 'provider']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('API Key Information', {
            'fields': ('organization', 'provider', 'is_active')
        }),
        ('Credentials', {
            'fields': ('api_key', 'api_secret'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Custom admin actions
@admin.action(description='Mark selected organizations as active')
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)
    modeladmin.message_user(request, f'{queryset.count()} organizations marked as active.')

@admin.action(description='Mark selected organizations as inactive')
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)
    modeladmin.message_user(request, f'{queryset.count()} organizations marked as inactive.')

@admin.action(description='Generate API keys for selected organizations')
def generate_api_keys(modeladmin, request, queryset):
    for org in queryset:
        # Generate OpenAI API key if not exists
        APIKey.objects.get_or_create(
            organization=org,
            provider='openai',
            defaults={'is_active': True}
        )
        # Generate Twilio API key if not exists
        APIKey.objects.get_or_create(
            organization=org,
            provider='twilio',
            defaults={'is_active': True}
        )
    modeladmin.message_user(request, f'API keys generated for {queryset.count()} organizations.')

# Add actions to OrganizationAdmin
OrganizationAdmin.actions = [make_active, make_inactive, generate_api_keys]
