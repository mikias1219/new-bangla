from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_interface, name='interface'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start/', views.start_conversation, name='start_conversation'),
    path('send-message/', views.send_message, name='send_message'),
    path('transfer/<int:conversation_id>/', views.transfer_conversation, name='transfer_conversation'),
    path('feedback/<int:conversation_id>/', views.submit_feedback, name='submit_feedback'),
]
