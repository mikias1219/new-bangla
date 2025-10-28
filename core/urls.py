from django.urls import path
from .views import (
    bangla_admin_dashboard, admin_api_dashboard_data, 
    admin_api_test_chat, admin_api_test_voice,
    AdminTestChatAPIView, AdminTestVoiceAPIView
)

urlpatterns = [
    # Custom Admin Dashboard
    path('', bangla_admin_dashboard, name='bangla_admin_dashboard'),
    
    # Admin API endpoints
    path('api/dashboard-data/', admin_api_dashboard_data, name='admin_dashboard_data'),
    path('api/test-chat/', admin_api_test_chat, name='admin_test_chat'),
    path('api/test-voice/', admin_api_test_voice, name='admin_test_voice'),
    
    # DRF API endpoints for admin testing
    path('api/test-chat-drf/', AdminTestChatAPIView.as_view(), name='admin_test_chat_drf'),
    path('api/test-voice-drf/', AdminTestVoiceAPIView.as_view(), name='admin_test_voice_drf'),
]
