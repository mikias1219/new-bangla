from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import json

from core.models import Client, BanglaConversation, CallLog, BanglaIntent, AdminProfile, SystemSettings, Analytics
from accounts.models import User, Organization, APIKey
from chat.models import Conversation, Message, AIAgent, Intent, Feedback
from voice.models import VoiceRecording, VoiceSession, SpeechSynthesis, VoiceAnalytics
from social_media.models import SocialMediaAccount, SocialMediaMessage, SocialMediaAutoReply, SocialMediaWebhook, SocialMediaAnalytics
from client_onboarding.models import ClientOnboardingStep, ClientSetupGuide, ClientSupportTicket, ClientFeedback
from services.openai_service import openai_service


def bangla_admin_dashboard(request):
    """Unified admin dashboard with all super admin features"""
    if not request.user.is_authenticated:
        return redirect('admin:login')
    
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser privileges required.')
        return redirect('admin:login')
    
    # Get dashboard statistics
    stats = {
        'total_users': User.objects.count(),
        'total_organizations': Organization.objects.count(),
        'total_conversations': BanglaConversation.objects.count(),
        'total_voice_calls': CallLog.objects.count(),
        'total_clients': Client.objects.count(),
        'total_ai_agents': AIAgent.objects.count(),
        'total_intents': BanglaIntent.objects.count(),
        'total_social_accounts': SocialMediaAccount.objects.count(),
        'total_support_tickets': ClientSupportTicket.objects.count(),
        'active_conversations': BanglaConversation.objects.filter(status='active').count(),
        'escalated_conversations': BanglaConversation.objects.filter(is_escalated=True).count(),
        'average_rating': BanglaConversation.objects.filter(satisfaction_rating__isnull=False).aggregate(
            avg_rating=Avg('satisfaction_rating')
        )['avg_rating'] or 0,
    }
    
    # Recent activity
    recent_conversations = BanglaConversation.objects.order_by('-created_at')[:10]
    recent_calls = CallLog.objects.order_by('-timestamp')[:10]
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # System settings
    system_settings = SystemSettings.objects.all()
    
    context = {
        'stats': stats,
        'recent_conversations': recent_conversations,
        'recent_calls': recent_calls,
        'recent_users': recent_users,
        'system_settings': system_settings,
        'user': request.user,
    }
    
    return render(request, 'admin/bangla_admin_dashboard.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class BanglaChatAPIView(View):
    """API view for Bangla chat functionality"""
    
    def post(self, request):
        """Handle chat message"""
        try:
            data = json.loads(request.body)
            client_id = data.get('client_id')
            user_name = data.get('user_name')
            message = data.get('message')
            
            if not all([client_id, user_name, message]):
                return JsonResponse({
                    'error': 'Missing required fields: client_id, user_name, message'
                }, status=400)
            
            try:
                client = Client.objects.get(id=client_id, is_active=True)
            except Client.DoesNotExist:
                return JsonResponse({
                    'error': 'Client not found or inactive'
                }, status=404)
            
            # Get conversation history for context
            recent_conversations = BanglaConversation.objects.filter(
                client=client,
                user_name=user_name
            ).order_by('-created_at')[:5]
            
            conversation_history = []
            for conv in reversed(recent_conversations):
                conversation_history.append({
                    'sender': 'user',
                    'content': conv.user_message
                })
                conversation_history.append({
                    'sender': 'ai',
                    'content': conv.ai_response
                })
            
            # Generate AI response using OpenAI service
            ai_result = openai_service.generate_chat_response(
                message=message,
                conversation_history=conversation_history,
                system_prompt=f"""
                আপনি {client.name} এর জন্য কাজ করছেন।
                সবসময় বাংলায় উত্তর দিন।
                বন্ধুত্বপূর্ণ এবং সহায়ক হন।
                """
            )
            
            # Create conversation record
            conversation = BanglaConversation.objects.create(
                client=client,
                user_name=user_name,
                user_message=message,
                ai_response=ai_result['response'],
                ai_confidence=ai_result.get('confidence', 0.0),
                intent_detected=ai_result.get('intent', '')
            )
            
            # Check if escalation is needed
            failed_responses = BanglaConversation.objects.filter(
                client=client,
                user_name=user_name,
                ai_confidence__lt=0.5
            ).count()
            
            if failed_responses >= 2:
                conversation.is_escalated = True
                conversation.escalated_at = timezone.now()
                conversation.status = 'escalated'
                conversation.save()
            
            response_data = {
                'conversation_id': conversation.id,
                'ai_response': ai_result['response'],
                'confidence': ai_result.get('confidence', 0.0),
                'is_escalated': conversation.is_escalated,
                'timestamp': conversation.created_at.isoformat()
            }
            
            return JsonResponse(response_data, status=201)
            
        except Exception as e:
            return JsonResponse({
                'error': f'Server error: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BanglaVoiceAPIView(View):
    """API view for voice processing"""
    
    def post(self, request):
        """Handle voice input and return audio response"""
        try:
            data = json.loads(request.body)
            client_id = data.get('client_id')
            caller_name = data.get('caller_name')
            question = data.get('question')
            
            if not all([client_id, caller_name, question]):
                return JsonResponse({
                    'error': 'Missing required fields: client_id, caller_name, question'
                }, status=400)
            
            try:
                client = Client.objects.get(id=client_id, is_active=True)
            except Client.DoesNotExist:
                return JsonResponse({
                    'error': 'Client not found or inactive'
                }, status=404)
            
            # Generate AI text response
            ai_result = openai_service.generate_chat_response(
                message=question,
                system_prompt=f"""
                আপনি {client.name} এর জন্য কাজ করছেন।
                সবসময় বাংলায় উত্তর দিন।
                সংক্ষিপ্ত এবং স্পষ্ট উত্তর দিন।
                """
            )
            
            # Generate audio response
            audio_result = openai_service.generate_voice_response(
                text=ai_result['response'],
                voice="alloy",
                model="tts-1"
            )
            
            # Create call log
            call_log = CallLog.objects.create(
                client=client,
                caller_name=caller_name,
                question=question,
                ai_text_response=ai_result['response'],
                ai_audio_response_url=audio_result.get('audio_url'),
                status='completed' if audio_result.get('audio_url') else 'failed',
                confidence_score=ai_result.get('confidence', 0.0),
                language_detected='bn'
            )
            
            response_data = {
                'call_id': call_log.id,
                'ai_text_response': ai_result['response'],
                'ai_audio_response_url': audio_result.get('audio_url'),
                'confidence': ai_result.get('confidence', 0.0),
                'timestamp': call_log.timestamp.isoformat()
            }
            
            if audio_result.get('error'):
                response_data['error'] = audio_result['error']
            
            return JsonResponse(response_data, status=201)
            
        except Exception as e:
            return JsonResponse({
                'error': f'Server error: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BanglaRatingAPIView(View):
    """API view for conversation rating"""
    
    def post(self, request):
        """Rate a conversation"""
        try:
            data = json.loads(request.body)
            conversation_id = data.get('conversation_id')
            rating = data.get('rating')
            
            if not all([conversation_id, rating]):
                return JsonResponse({
                    'error': 'Missing required fields: conversation_id, rating'
                }, status=400)
            
            try:
                rating = int(rating)
                if not (1 <= rating <= 5):
                    raise ValueError("Rating must be between 1 and 5")
            except ValueError as e:
                return JsonResponse({
                    'error': str(e)
                }, status=400)
            
            try:
                conversation = BanglaConversation.objects.get(id=conversation_id)
            except BanglaConversation.DoesNotExist:
                return JsonResponse({
                    'error': 'Conversation not found'
                }, status=404)
            
            conversation.satisfaction_rating = rating
            conversation.save()
            
            return JsonResponse({
                'message': 'Rating saved successfully',
                'conversation_id': conversation.id,
                'rating': rating
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Server error: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BanglaHandoffAPIView(View):
    """API view for human handoff"""
    
    def post(self, request):
        """Request human handoff"""
        try:
            data = json.loads(request.body)
            conversation_id = data.get('conversation_id')
            reason = data.get('reason', 'User requested human help')
            
            if not conversation_id:
                return JsonResponse({
                    'error': 'Missing required field: conversation_id'
                }, status=400)
            
            try:
                conversation = BanglaConversation.objects.get(id=conversation_id)
            except BanglaConversation.DoesNotExist:
                return JsonResponse({
                    'error': 'Conversation not found'
                }, status=404)
            
            conversation.is_escalated = True
            conversation.escalated_at = timezone.now()
            conversation.status = 'escalated'
            conversation.save()
            
            return JsonResponse({
                'message': 'Human handoff requested successfully',
                'conversation_id': conversation.id,
                'escalated_at': conversation.escalated_at.isoformat()
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Server error: {str(e)}'
            }, status=500)


# Admin API endpoints for the dashboard
@login_required
def admin_api_dashboard_data(request):
    """Get dashboard data for admin"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get statistics
    stats = {
        'total_users': User.objects.count(),
        'total_organizations': Organization.objects.count(),
        'total_conversations': BanglaConversation.objects.count(),
        'total_voice_calls': CallLog.objects.count(),
        'total_clients': Client.objects.count(),
        'active_conversations': BanglaConversation.objects.filter(status='active').count(),
        'escalated_conversations': BanglaConversation.objects.filter(is_escalated=True).count(),
    }
    
    return JsonResponse(stats)


@csrf_exempt
@login_required
def admin_api_test_chat(request):
    """Test chat functionality from admin dashboard"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', 'Hello')
        client_id = data.get('client_id', 1)
        
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return JsonResponse({'error': 'Client not found'}, status=404)
        
        # Test AI response
        ai_result = openai_service.generate_chat_response(
            message=message,
            system_prompt=f"Test message for {client.name}. Respond in Bangla."
        )
        
        return JsonResponse({
            'message': message,
            'ai_response': ai_result['response'],
            'confidence': ai_result.get('confidence', 0.0),
            'client': client.name
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
@login_required
def admin_api_test_voice(request):
    """Test voice functionality from admin dashboard"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data.get('text', 'Hello, this is a test.')
        
        # Test voice synthesis
        audio_result = openai_service.generate_voice_response(
            text=text,
            voice="alloy",
            model="tts-1"
        )
        
        return JsonResponse({
            'text': text,
            'audio_url': audio_result.get('audio_url'),
            'status': 'success' if audio_result.get('audio_url') else 'failed',
            'error': audio_result.get('error')
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)