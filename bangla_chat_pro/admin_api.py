from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from accounts.models import Organization, User
from chat.models import Conversation, Message, AIAgent
from voice.models import VoiceSession, VoiceRecording
from social_media.models import SocialMediaAccount, SocialMediaMessage
from client_onboarding.models import ClientOnboardingStep, ClientSupportTicket


@login_required
def custom_admin_dashboard(request):
    """Main custom admin dashboard view"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get statistics
    total_organizations = Organization.objects.count()
    pending_approvals = Organization.objects.filter(approval_status='pending').count()
    total_users = User.objects.count()
    total_conversations = Conversation.objects.count()
    
    # Get pending organizations
    pending_organizations = Organization.objects.filter(approval_status='pending').order_by('-created_at')[:10]
    
    context = {
        'total_organizations': total_organizations,
        'pending_approvals': pending_approvals,
        'total_users': total_users,
        'total_conversations': total_conversations,
        'pending_organizations': pending_organizations,
    }
    
    return render(request, 'admin/unified_admin_dashboard.html', context)


@login_required
@csrf_exempt
def dashboard_data_api(request):
    """API endpoint for dashboard statistics"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'GET':
        data = {
            'total_organizations': Organization.objects.count(),
            'pending_approvals': Organization.objects.filter(approval_status='pending').count(),
            'total_users': User.objects.count(),
            'total_conversations': Conversation.objects.count(),
            'active_ai_agents': AIAgent.objects.filter(status='active').count(),
            'total_voice_sessions': VoiceSession.objects.count(),
            'total_social_accounts': SocialMediaAccount.objects.count(),
            'open_support_tickets': ClientSupportTicket.objects.filter(status='open').count(),
        }
        return JsonResponse(data)


@login_required
@csrf_exempt
def organizations_api(request):
    """API endpoint for organizations management"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'GET':
        organizations = Organization.objects.annotate(
            user_count=Count('users')
        ).order_by('-created_at')
        
        data = []
        for org in organizations:
            data.append({
                'id': org.id,
                'name': org.name,
                'description': org.description,
                'contact_email': org.contact_email,
                'subscription_plan': org.subscription_plan,
                'is_active': org.is_active,
                'approval_status': org.approval_status,
                'user_count': org.user_count,
                'created_at': org.created_at.isoformat(),
            })
        
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            organization = Organization.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                contact_email=data['contact_email'],
                subscription_plan=data.get('subscription_plan', 'free'),
                max_users=data.get('max_users', 10),
                approval_status='approved',  # Auto-approve admin-created orgs
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'organization_id': organization.id
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@login_required
@csrf_exempt
def users_api(request):
    """API endpoint for users management"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'GET':
        users = User.objects.select_related('organization').order_by('-date_joined')
        
        data = []
        for user in users:
            data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'organization': {
                    'id': user.organization.id,
                    'name': user.organization.name
                } if user.organization else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'date_joined': user.date_joined.isoformat(),
            })
        
        return JsonResponse(data, safe=False)


@login_required
@csrf_exempt
def conversations_api(request):
    """API endpoint for conversations management"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'GET':
        conversations = Conversation.objects.select_related(
            'user', 'organization', 'ai_agent'
        ).order_by('-last_message_at')
        
        data = []
        for conv in conversations:
            data.append({
                'id': conv.id,
                'user': {
                    'id': conv.user.id,
                    'username': conv.user.username
                },
                'organization': {
                    'id': conv.organization.id,
                    'name': conv.organization.name
                } if conv.organization else None,
                'ai_agent': {
                    'id': conv.ai_agent.id,
                    'name': conv.ai_agent.name
                } if conv.ai_agent else None,
                'status': conv.status,
                'message_count': conv.message_count,
                'ai_responses': conv.ai_responses,
                'started_at': conv.started_at.isoformat(),
                'last_message_at': conv.last_message_at.isoformat() if conv.last_message_at else None,
            })
        
        return JsonResponse(data, safe=False)


@login_required
@csrf_exempt
def ai_agents_api(request):
    """API endpoint for AI agents management"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'GET':
        ai_agents = AIAgent.objects.select_related('organization').order_by('-created_at')
        
        data = []
        for agent in ai_agents:
            data.append({
                'id': agent.id,
                'name': agent.name,
                'description': agent.description,
                'organization': {
                    'id': agent.organization.id,
                    'name': agent.organization.name
                } if agent.organization else None,
                'status': agent.status,
                'model_provider': agent.model_provider,
                'model_name': agent.model_name,
                'temperature': agent.temperature,
                'max_tokens': agent.max_tokens,
                'total_conversations': agent.total_conversations,
                'total_messages': agent.total_messages,
                'average_rating': agent.average_rating,
                'created_at': agent.created_at.isoformat(),
            })
        
        return JsonResponse(data, safe=False)


@login_required
@csrf_exempt
def approve_organization_api(request, org_id):
    """API endpoint to approve organization"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        try:
            organization = Organization.objects.get(id=org_id)
            organization.approval_status = 'approved'
            organization.approved_by = request.user
            organization.approved_at = timezone.now()
            organization.is_active = True
            organization.save()
            
            return JsonResponse({'success': True, 'message': 'Organization approved successfully'})
        except Organization.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Organization not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
def reject_organization_api(request, org_id):
    """API endpoint to reject organization"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reason = data.get('reason', '')
            
            organization = Organization.objects.get(id=org_id)
            organization.approval_status = 'rejected'
            organization.approved_by = request.user
            organization.approved_at = timezone.now()
            organization.rejection_reason = reason
            organization.is_active = False
            organization.save()
            
            return JsonResponse({'success': True, 'message': 'Organization rejected successfully'})
        except Organization.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Organization not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
def voice_sessions_api(request):
    """API endpoint for voice sessions"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'GET':
        sessions = VoiceSession.objects.select_related('user').order_by('-started_at')
        
        data = []
        for session in sessions:
            data.append({
                'id': session.id,
                'session_id': session.session_id,
                'user': {
                    'id': session.user.id,
                    'username': session.user.username
                },
                'status': session.status,
                'voice_type': session.voice_type,
                'language': session.language,
                'total_recordings': session.total_recordings,
                'started_at': session.started_at.isoformat(),
                'ended_at': session.ended_at.isoformat() if session.ended_at else None,
            })
        
        return JsonResponse(data, safe=False)


@login_required
@csrf_exempt
def voice_recordings_api(request):
    """API endpoint for voice recordings"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'GET':
        recordings = VoiceRecording.objects.select_related('user').order_by('-created_at')
        
        data = []
        for recording in recordings:
            data.append({
                'id': recording.id,
                'user': {
                    'id': recording.user.id,
                    'username': recording.user.username
                },
                'status': recording.status,
                'duration': recording.duration,
                'file_format': recording.file_format,
                'transcription': recording.transcription,
                'confidence_score': recording.confidence_score,
                'created_at': recording.created_at.isoformat(),
            })
        
        return JsonResponse(data, safe=False)


@login_required
@csrf_exempt
def social_accounts_api(request):
    """API endpoint for social media accounts"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'GET':
        accounts = SocialMediaAccount.objects.select_related('organization').order_by('-created_at')
        
        data = []
        for account in accounts:
            data.append({
                'id': account.id,
                'platform': account.platform,
                'account_name': account.account_name,
                'organization': {
                    'id': account.organization.id,
                    'name': account.organization.name
                },
                'is_active': account.is_active,
                'auto_reply_enabled': account.auto_reply_enabled,
                'created_at': account.created_at.isoformat(),
            })
        
        return JsonResponse(data, safe=False)


@login_required
@csrf_exempt
def social_messages_api(request):
    """API endpoint for social media messages"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'GET':
        messages = SocialMediaMessage.objects.select_related(
            'social_account', 'organization'
        ).order_by('-received_at')
        
        data = []
        for message in messages:
            data.append({
                'id': message.id,
                'platform': message.social_account.platform,
                'sender_id': message.sender_id,
                'sender_name': message.sender_name,
                'message_type': message.message_type,
                'content': message.content[:100] + '...' if len(message.content) > 100 else message.content,
                'ai_processed': message.ai_processed,
                'received_at': message.received_at.isoformat(),
            })
        
        return JsonResponse(data, safe=False)


@login_required
@csrf_exempt
def onboarding_steps_api(request):
    """API endpoint for onboarding steps"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'GET':
        steps = ClientOnboardingStep.objects.select_related('organization').order_by('-created_at')
        
        data = []
        for step in steps:
            data.append({
                'id': step.id,
                'organization': {
                    'id': step.organization.id,
                    'name': step.organization.name
                },
                'step_name': step.step_name,
                'is_completed': step.is_completed,
                'completed_at': step.completed_at.isoformat() if step.completed_at else None,
                'notes': step.notes,
                'created_at': step.created_at.isoformat(),
            })
        
        return JsonResponse(data, safe=False)


@login_required
@csrf_exempt
def support_tickets_api(request):
    """API endpoint for support tickets"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'GET':
        tickets = ClientSupportTicket.objects.select_related(
            'organization', 'created_by', 'assigned_to'
        ).order_by('-created_at')
        
        data = []
        for ticket in tickets:
            data.append({
                'id': ticket.id,
                'title': ticket.title,
                'description': ticket.description,
                'organization': {
                    'id': ticket.organization.id,
                    'name': ticket.organization.name
                },
                'priority': ticket.priority,
                'status': ticket.status,
                'created_by': {
                    'id': ticket.created_by.id,
                    'username': ticket.created_by.username
                },
                'assigned_to': {
                    'id': ticket.assigned_to.id,
                    'username': ticket.assigned_to.username
                } if ticket.assigned_to else None,
                'created_at': ticket.created_at.isoformat(),
                'resolved_at': ticket.resolved_at.isoformat() if ticket.resolved_at else None,
            })
        
        return JsonResponse(data, safe=False)
