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
]
