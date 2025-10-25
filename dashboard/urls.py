from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard_home, name='home'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('conversations/', views.conversations_view, name='conversations'),
    path('agent-management/', views.agent_management, name='agent_management'),
    path('system-settings/', views.system_settings, name='system_settings'),
    path('intents-training/', views.intents_training, name='intents_training'),
    path('review-ratings/', views.review_ratings, name='review_ratings'),
    path('security-logs/', views.security_logs, name='security_logs'),
]
