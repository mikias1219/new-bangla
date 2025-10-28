"""
URL configuration for bangla_chat_pro project.

Clean, organized URL structure for BanglaChatPro
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin (keep for superuser access)
    path('admin/', admin.site.urls),
    
    # Main Public Dashboard (Root URL)
    path('', include('accounts.urls')),
    
    # BanglaChatPro Core API Endpoints
    path('api/', include('api.urls')),  # All API endpoints under /api/
    
    # Admin Dashboard (Custom)
    path('admin-dashboard/', include('core.urls')),  # Custom admin dashboard
    
    # Chat Interface (Only after login)
    path('chat/', include('chat.urls')),  # Chat interface moved to /chat/
    
    # Additional Features (if needed)
    path('voice/', include('voice.urls')),  # Voice features
    path('social/', include('social_media.urls')),  # Social media integration
    path('onboarding/', include('client_onboarding.urls')),  # Client onboarding
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)