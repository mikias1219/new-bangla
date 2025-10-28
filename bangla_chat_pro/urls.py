"""
URL configuration for bangla_chat_pro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from bangla_chat_pro.admin_api import (
    custom_admin_dashboard, dashboard_data_api, organizations_api, users_api,
    conversations_api, ai_agents_api, approve_organization_api, reject_organization_api,
    voice_sessions_api, voice_recordings_api, social_accounts_api, social_messages_api,
    onboarding_steps_api, support_tickets_api
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Unified Admin Dashboard
    path('admin-dashboard/', custom_admin_dashboard, name='unified_admin_dashboard'),
    path('admin/api/dashboard-data/', dashboard_data_api, name='dashboard_data_api'),
    path('admin/api/organizations/', organizations_api, name='organizations_api'),
    path('admin/api/users/', users_api, name='users_api'),
    path('admin/api/conversations/', conversations_api, name='conversations_api'),
    path('admin/api/ai-agents/', ai_agents_api, name='ai_agents_api'),
    path('admin/api/approve-organization/<int:org_id>/', approve_organization_api, name='approve_organization_api'),
    path('admin/api/reject-organization/<int:org_id>/', reject_organization_api, name='reject_organization_api'),
    path('admin/api/voice-sessions/', voice_sessions_api, name='voice_sessions_api'),
    path('admin/api/voice-recordings/', voice_recordings_api, name='voice_recordings_api'),
    path('admin/api/social-accounts/', social_accounts_api, name='social_accounts_api'),
    path('admin/api/social-messages/', social_messages_api, name='social_messages_api'),
    path('admin/api/onboarding-steps/', onboarding_steps_api, name='onboarding_steps_api'),
    path('admin/api/support-tickets/', support_tickets_api, name='support_tickets_api'),
    
    path('api/', include('api.urls')),
    path('', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chat.urls')),
    path('voice/', include('voice.urls')),
    path('social/', include('social_media.urls')),
    path('onboarding/', include('client_onboarding.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
