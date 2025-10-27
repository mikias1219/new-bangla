from django.urls import path
from . import views

app_name = 'voice'

urlpatterns = [
    path('', views.voice_interface, name='interface'),
    path('upload/', views.upload_voice_recording, name='upload'),
    path('synthesize/', views.synthesize_speech, name='synthesize'),
    path('session/start/', views.start_voice_session, name='start_session'),
    path('session/end/', views.end_voice_session, name='end_session'),
    path('recording/<int:recording_id>/', views.recording_detail, name='recording_detail'),

    # Twilio webhooks (no auth required)
    path('twilio/voice/<int:organization_id>/', views.twilio_voice_webhook, name='twilio_voice'),
    path('twilio/speech/<int:organization_id>/', views.twilio_speech_process, name='twilio_speech'),
    path('twilio/sms/<int:organization_id>/', views.twilio_sms_webhook, name='twilio_sms'),

    # Manual call/SMS initiation
    path('call/initiate/', views.initiate_call, name='initiate_call'),
    path('sms/send/', views.send_sms, name='send_sms'),
]
