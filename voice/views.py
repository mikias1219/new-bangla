from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import VoiceRecording, VoiceSession, SpeechSynthesis
from services.twilio_service import TwilioService
from accounts.models import Organization
import json

@login_required
def voice_interface(request):
    """Voice interface view"""
    # Get active voice session or create new one
    session, created = VoiceSession.objects.get_or_create(
        user=request.user,
        status='active',
        defaults={
            'conversation': None,  # Will be set when conversation starts
            'session_id': f"voice_{request.user.id}_{timezone.now().timestamp()}"
        }
    )

    # Get recent recordings
    recordings = VoiceRecording.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    context = {
        'voice_session': session,
        'recordings': recordings,
    }

    return render(request, 'voice/interface.html', context)

@login_required
@csrf_exempt
def upload_voice_recording(request):
    """Upload voice recording"""
    if request.method == 'POST':
        audio_file = request.FILES.get('audio')
        conversation_id = request.POST.get('conversation_id')

        if not audio_file:
            return JsonResponse({'error': 'No audio file provided'}, status=400)

        try:
            # Create voice recording
            recording = VoiceRecording.objects.create(
                user=request.user,
                conversation_id=conversation_id if conversation_id else None,
                audio_file=audio_file,
                file_size=audio_file.size,
                status='processing'
            )

            # Mock voice processing (in production, this would call your voice service)
            recording.status = 'completed'
            recording.transcription = "This is a mock transcription of the voice recording."
            recording.confidence_score = 0.92
            recording.detected_language = 'en'
            recording.language_confidence = 0.95
            recording.save()

            return JsonResponse({
                'success': True,
                'recording_id': recording.id,
                'transcription': recording.transcription,
                'confidence': recording.confidence_score
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
@csrf_exempt
def synthesize_speech(request):
    """Synthesize speech from text"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text')
            message_id = data.get('message_id')

            if not text:
                return JsonResponse({'error': 'Text is required'}, status=400)

            # Create speech synthesis record
            synthesis = SpeechSynthesis.objects.create(
                user=request.user,
                message_id=message_id if message_id else None,
                status='processing'
            )

            # Mock speech synthesis (in production, this would call TTS service)
            synthesis.status = 'completed'
            synthesis.duration = len(text) * 0.1  # Rough estimate
            synthesis.save()

            return JsonResponse({
                'success': True,
                'synthesis_id': synthesis.id,
                'duration': synthesis.duration
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def start_voice_session(request):
    """Start a new voice session"""
    if request.method == 'POST':
        # End any existing active sessions
        VoiceSession.objects.filter(
            user=request.user,
            status='active'
        ).update(status='completed', ended_at=timezone.now())

        # Create new session
        session = VoiceSession.objects.create(
            user=request.user,
            session_id=f"voice_{request.user.id}_{timezone.now().timestamp()}",
            voice_type=request.POST.get('voice_type', 'neutral'),
            language=request.POST.get('language', 'en'),
            speed=float(request.POST.get('speed', 1.0))
        )

        return JsonResponse({
            'success': True,
            'session_id': session.session_id
        })

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def end_voice_session(request):
    """End voice session"""
    if request.method == 'POST':
        session_id = request.POST.get('session_id')

        if session_id:
            session = get_object_or_404(VoiceSession, session_id=session_id, user=request.user)
            session.status = 'completed'
            session.ended_at = timezone.now()
            session.save()

            return JsonResponse({'success': True})

    return JsonResponse({'error': 'Session ID required'}, status=400)

@login_required
def recording_detail(request, recording_id):
    """Voice recording detail view"""
    recording = get_object_or_404(VoiceRecording, id=recording_id, user=request.user)

    context = {
        'recording': recording,
    }

    return render(request, 'voice/recording_detail.html', context)


# Twilio Webhook Views (No authentication required for webhooks)
@csrf_exempt
@require_POST
def twilio_voice_webhook(request, organization_id):
    """Handle incoming Twilio voice calls"""
    try:
        organization = Organization.objects.get(id=organization_id)

        twilio_service = TwilioService(organization)
        twiml_response = twilio_service.generate_twiml(request.POST, organization_id)

        return HttpResponse(twiml_response, content_type='text/xml')

    except Organization.DoesNotExist:
        return HttpResponse('<Response><Say>Organization not found.</Say></Response>', content_type='text/xml')
    except Exception as e:
        return HttpResponse(f'<Response><Say>Error: {str(e)}</Say></Response>', content_type='text/xml')


@csrf_exempt
@require_POST
def twilio_speech_process(request, organization_id):
    """Process speech input from Twilio calls"""
    try:
        organization = Organization.objects.get(id=organization_id)

        twilio_service = TwilioService(organization)
        twiml_response = twilio_service.process_speech(request.POST, organization_id)

        return HttpResponse(twiml_response, content_type='text/xml')

    except Organization.DoesNotExist:
        return HttpResponse('<Response><Say>Organization not found.</Say></Response>', content_type='text/xml')
    except Exception as e:
        return HttpResponse(f'<Response><Say>Error: {str(e)}</Say></Response>', content_type='text/xml')


@csrf_exempt
@require_POST
def twilio_sms_webhook(request, organization_id):
    """Handle incoming Twilio SMS messages"""
    try:
        organization = Organization.objects.get(id=organization_id)

        # Get message details
        from_number = request.POST.get('From')
        to_number = request.POST.get('To')
        message_body = request.POST.get('Body')
        message_sid = request.POST.get('MessageSid')

        # Process SMS with AI (similar to voice processing)
        twilio_service = TwilioService(organization)

        # For SMS, we'll create a simple conversation and respond
        conversation = twilio_service._get_or_create_voice_conversation(from_number, organization_id)

        # Create user message
        from chat.models import Message
        Message.objects.create(
            conversation=conversation,
            sender_type='user',
            sender=conversation.user,
            content=f"SMS: {message_body}"
        )

        # Generate AI response
        ai_response = twilio_service._process_with_ai(conversation, message_body)

        # Send SMS response
        twilio_service.send_sms(from_number, ai_response)

        # Create AI message
        Message.objects.create(
            conversation=conversation,
            sender_type='ai',
            content=ai_response
        )

        return HttpResponse('', content_type='text/xml')  # Twilio expects empty response for SMS

    except Exception as e:
        # Log error but return empty response to Twilio
        print(f"Twilio SMS error: {e}")
        return HttpResponse('', content_type='text/xml')


@login_required
def initiate_call(request):
    """Initiate outbound call (for testing/admin)"""
    if request.method == 'POST':
        to_number = request.POST.get('to_number')
        organization = request.user.organization

        if not organization:
            messages.error(request, 'No organization associated with your account.')
            return redirect('voice:interface')

        try:
            twilio_service = TwilioService(organization)
            call_sid = twilio_service.make_call(to_number)

            messages.success(request, f'Call initiated successfully. Call SID: {call_sid}')
        except Exception as e:
            messages.error(request, f'Failed to initiate call: {str(e)}')

    return redirect('voice:interface')


@login_required
def send_sms(request):
    """Send SMS message (for testing/admin)"""
    if request.method == 'POST':
        to_number = request.POST.get('to_number')
        message = request.POST.get('message')
        organization = request.user.organization

        if not organization:
            messages.error(request, 'No organization associated with your account.')
            return redirect('voice:interface')

        try:
            twilio_service = TwilioService(organization)
            message_sid = twilio_service.send_sms(to_number, message)

            messages.success(request, f'SMS sent successfully. Message SID: {message_sid}')
        except Exception as e:
            messages.error(request, f'Failed to send SMS: {str(e)}')

    return redirect('voice:interface')