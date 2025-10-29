from django.urls import path, include
from . import views

app_name = 'chat'

urlpatterns = [
    # Main BanglaChatPro Chat Interface
    path('', views.bangla_chat_view, name='bangla_chat'),
    
    # Additional chat features
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start/', views.start_conversation, name='start_conversation'),
]