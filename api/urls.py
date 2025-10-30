from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    chat_send, voice_process, rate_conversation, request_human_handoff,
    get_order_status, manage_clients, manage_intents, client_detail, intent_detail,
    get_product_availability, get_payment_status, get_client_feature_status,
    products_crud, product_detail
)
from rest_framework.authtoken.views import obtain_auth_token

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
    path('products/availability/', get_product_availability, name='bangla_product_availability'),
    path('products/', products_crud, name='bangla_products_crud'),
    path('products/<int:product_id>/', product_detail, name='bangla_product_detail'),
    path('payments/status/', get_payment_status, name='bangla_payment_status'),
    path('client/features/', get_client_feature_status, name='bangla_client_feature_status'),
    path('clients/', manage_clients, name='bangla_manage_clients'),
    path('clients/<int:client_id>/', client_detail, name='bangla_client_detail'),
    path('intents/', manage_intents, name='bangla_manage_intents'),
    path('intents/<int:intent_id>/', intent_detail, name='bangla_intent_detail'),

    # Auth
    path('token/', obtain_auth_token, name='api_obtain_token'),
]
