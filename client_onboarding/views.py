from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from .models import ClientOnboardingStep, ClientSetupGuide, ClientSupportTicket, ClientFeedback
from accounts.models import Organization, APIKey
from chat.models import AIAgent
import json


@login_required
def onboarding_dashboard(request):
    """Main onboarding dashboard"""
    organization = request.user.organization
    
    if not organization:
        messages.error(request, 'No organization associated with your account.')
        return redirect('accounts:profile')
    
    # Get onboarding steps
    steps = ClientOnboardingStep.objects.filter(organization=organization)
    
    # Calculate progress
    total_steps = len(ClientOnboardingStep.STEP_CHOICES)
    completed_steps = steps.filter(is_completed=True).count()
    progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
    
    # Get setup guides
    setup_guides = ClientSetupGuide.objects.filter(is_active=True)
    
    # Get recent support tickets
    recent_tickets = ClientSupportTicket.objects.filter(
        organization=organization
    ).order_by('-created_at')[:5]
    
    context = {
        'steps': steps,
        'progress_percentage': progress_percentage,
        'completed_steps': completed_steps,
        'total_steps': total_steps,
        'setup_guides': setup_guides,
        'recent_tickets': recent_tickets,
    }
    
    return render(request, 'client_onboarding/dashboard.html', context)


@login_required
def onboarding_step(request, step_name):
    """Handle individual onboarding steps"""
    organization = request.user.organization
    
    if not organization:
        messages.error(request, 'No organization associated with your account.')
        return redirect('accounts:profile')
    
    # Get or create the step
    step, created = ClientOnboardingStep.objects.get_or_create(
        organization=organization,
        step_name=step_name,
        defaults={'is_completed': False}
    )
    
    if request.method == 'POST':
        # Handle step completion
        if request.POST.get('complete_step'):
            step.complete_step()
            messages.success(request, f'Step "{step.get_step_name_display()}" completed successfully!')
            return redirect('client_onboarding:dashboard')
    
    # Get relevant data based on step
    context = {
        'step': step,
        'step_name': step_name,
    }
    
    if step_name == 'api_keys':
        context['api_keys'] = APIKey.objects.filter(organization=organization)
    elif step_name == 'ai_agent':
        context['ai_agents'] = AIAgent.objects.filter(organization=organization)
    elif step_name == 'social_media':
        from social_media.models import SocialMediaAccount
        context['social_accounts'] = SocialMediaAccount.objects.filter(organization=organization)
    
    return render(request, f'client_onboarding/steps/{step_name}.html', context)


@login_required
def setup_guide(request, service_name):
    """View setup guide for a specific service"""
    guide = get_object_or_404(ClientSetupGuide, service_name=service_name, is_active=True)
    
    context = {
        'guide': guide,
    }
    
    return render(request, 'client_onboarding/setup_guide.html', context)


@login_required
def create_support_ticket(request):
    """Create a new support ticket"""
    organization = request.user.organization
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority', 'medium')
        
        if title and description:
            ticket = ClientSupportTicket.objects.create(
                organization=organization,
                title=title,
                description=description,
                priority=priority,
                created_by=request.user
            )
            
            messages.success(request, 'Support ticket created successfully!')
            return redirect('client_onboarding:dashboard')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'client_onboarding/create_ticket.html')


@login_required
def support_tickets(request):
    """List all support tickets for the organization"""
    organization = request.user.organization
    tickets = ClientSupportTicket.objects.filter(
        organization=organization
    ).order_by('-created_at')
    
    context = {
        'tickets': tickets,
    }
    
    return render(request, 'client_onboarding/support_tickets.html', context)


@login_required
def ticket_detail(request, ticket_id):
    """View support ticket details"""
    organization = request.user.organization
    ticket = get_object_or_404(
        ClientSupportTicket,
        id=ticket_id,
        organization=organization
    )
    
    context = {
        'ticket': ticket,
    }
    
    return render(request, 'client_onboarding/ticket_detail.html', context)


@login_required
@csrf_exempt
def submit_feedback(request):
    """Submit feedback for onboarding steps"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            step_name = data.get('step_name')
            rating = data.get('rating')
            feedback_text = data.get('feedback_text', '')
            suggestions = data.get('suggestions', '')
            
            organization = request.user.organization
            
            if organization and step_name and rating:
                feedback = ClientFeedback.objects.create(
                    organization=organization,
                    step_name=step_name,
                    rating=rating,
                    feedback_text=feedback_text,
                    suggestions=suggestions
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Feedback submitted successfully!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required fields'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def quick_setup(request):
    """Quick setup wizard for new clients"""
    organization = request.user.organization
    
    if request.method == 'POST':
        # Handle quick setup form
        setup_data = {
            'openai_api_key': request.POST.get('openai_api_key'),
            'twilio_account_sid': request.POST.get('twilio_account_sid'),
            'twilio_auth_token': request.POST.get('twilio_auth_token'),
            'facebook_page_id': request.POST.get('facebook_page_id'),
            'facebook_access_token': request.POST.get('facebook_access_token'),
        }
        
        try:
            with transaction.atomic():
                # Create API keys
                if setup_data['openai_api_key']:
                    APIKey.objects.get_or_create(
                        organization=organization,
                        provider='openai',
                        defaults={
                            'api_key': setup_data['openai_api_key'],
                            'is_active': True
                        }
                    )
                
                if setup_data['twilio_account_sid'] and setup_data['twilio_auth_token']:
                    APIKey.objects.get_or_create(
                        organization=organization,
                        provider='twilio',
                        defaults={
                            'api_key': setup_data['twilio_account_sid'],
                            'api_secret': setup_data['twilio_auth_token'],
                            'is_active': True
                        }
                    )
                
                # Mark relevant steps as completed
                steps_to_complete = ['api_keys']
                if setup_data['facebook_page_id']:
                    steps_to_complete.append('social_media')
                
                for step_name in steps_to_complete:
                    step, created = ClientOnboardingStep.objects.get_or_create(
                        organization=organization,
                        step_name=step_name,
                        defaults={'is_completed': False}
                    )
                    step.complete_step()
                
                messages.success(request, 'Quick setup completed successfully!')
                return redirect('client_onboarding:dashboard')
                
        except Exception as e:
            messages.error(request, f'Setup failed: {str(e)}')
    
    return render(request, 'client_onboarding/quick_setup.html')


@login_required
def onboarding_complete(request):
    """Mark onboarding as complete"""
    organization = request.user.organization
    
    # Mark all steps as completed
    for step_name, _ in ClientOnboardingStep.STEP_CHOICES:
        step, created = ClientOnboardingStep.objects.get_or_create(
            organization=organization,
            step_name=step_name,
            defaults={'is_completed': False}
        )
        step.complete_step()
    
    messages.success(request, 'Congratulations! Your onboarding is now complete!')
    return redirect('client_onboarding:dashboard')