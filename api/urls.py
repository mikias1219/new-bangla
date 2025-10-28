from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    chat_send, voice_process, rate_conversation, request_human_handoff,
    get_order_status, manage_clients, manage_intents
)

router = DefaultRouter()

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    
    # BanglaChatPro Core API Endpoints
    path('chat/', chat_send, name='bangla_chat_send'),
    path('voice/', voice_process, name='bangla_voice_process'),
    path('rate/', rate_conversation, name='bangla_rate_conversation'),
    path('handoff/', request_human_handoff, name='bangla_request_human_handoff'),
    path('orders/<int:order_id>/', get_order_status, name='bangla_get_order_status'),
    path('clients/', manage_clients, name='bangla_manage_clients'),
    path('intents/', manage_intents, name='bangla_manage_intents'),
]
