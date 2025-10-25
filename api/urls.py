from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'conversations', views.ConversationViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'ai-agents', views.AIAgentViewSet)
router.register(r'organizations', views.OrganizationViewSet)
router.register(r'analytics', views.AnalyticsViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', views.token_view, name='token'),
    path('auth/me/', views.current_user, name='current_user'),
    path('voice/process/', views.process_voice, name='process_voice'),
    path('chat/send/', views.send_chat_message, name='send_chat_message'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
]
