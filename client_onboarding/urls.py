from django.urls import path
from . import views

app_name = 'client_onboarding'

urlpatterns = [
    path('', views.onboarding_dashboard, name='dashboard'),
    path('step/<str:step_name>/', views.onboarding_step, name='step'),
    path('guide/<str:service_name>/', views.setup_guide, name='setup_guide'),
    path('quick-setup/', views.quick_setup, name='quick_setup'),
    path('complete/', views.onboarding_complete, name='complete'),
    
    # Support tickets
    path('tickets/', views.support_tickets, name='support_tickets'),
    path('tickets/create/', views.create_support_ticket, name='create_ticket'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    
    # API endpoints
    path('api/feedback/', views.submit_feedback, name='submit_feedback'),
]
