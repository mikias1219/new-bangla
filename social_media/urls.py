from django.urls import path
from . import views

app_name = 'social_media'

urlpatterns = [
    # Webhook endpoints (no auth required)
    path('webhook/facebook/<int:organization_id>/', views.facebook_webhook, name='facebook_webhook'),
    path('webhook/twitter/<int:organization_id>/', views.twitter_webhook, name='twitter_webhook'),
    path('webhook/instagram/<int:organization_id>/', views.instagram_webhook, name='instagram_webhook'),
    path('webhook/whatsapp/<int:organization_id>/', views.whatsapp_webhook, name='whatsapp_webhook'),

    # Social media account management
    path('accounts/', views.social_accounts_list, name='accounts_list'),
    path('accounts/connect/<str:platform>/', views.connect_account, name='connect_account'),
    path('accounts/<int:account_id>/', views.account_detail, name='account_detail'),
    path('accounts/<int:account_id>/disconnect/', views.disconnect_account, name='disconnect_account'),

    # Messages and conversations
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),

    # Auto-replies
    path('auto-replies/', views.auto_replies_list, name='auto_replies_list'),
    path('auto-replies/create/', views.create_auto_reply, name='create_auto_reply'),
    path('auto-replies/<int:reply_id>/edit/', views.edit_auto_reply, name='edit_auto_reply'),
    path('auto-replies/<int:reply_id>/delete/', views.delete_auto_reply, name='delete_auto_reply'),

    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('analytics/export/', views.export_analytics, name='export_analytics'),
]
