from django.http import HttpResponse

def landing_page(request):
    """Landing page - public view"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'landing.html')

# Import other modules after the landing_page function to avoid circular imports
try:
    from django.shortcuts import render, redirect, get_object_or_404
    from django.contrib.auth.decorators import login_required
    from django.contrib import messages
    from django.db.models import Count, Avg, Sum, Q
    from django.db.models.functions import TruncDate
    from django.utils import timezone
    from datetime import timedelta
    from .models import Analytics, SystemSetting, LogEntry, Notification
    from accounts.models import Organization, User
    from chat.models import Conversation, Message, AIAgent, Feedback
    from voice.models import VoiceRecording, VoiceSession
except ImportError:
    # Handle case where Django models can't be imported yet
    pass

@login_required
def dashboard_home(request):
    """Main dashboard view"""
    user = request.user
    organization = user.organization

    if not organization:
        messages.error(request, "You are not associated with any organization.")
        return redirect('accounts:login')

    # Get recent analytics
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)

    analytics_data = Analytics.objects.filter(
        organization=organization,
        date__gte=last_30_days
    ).aggregate(
        total_conversations=Sum('total_conversations'),
        active_conversations=Sum('active_conversations'),
        total_messages=Sum('total_messages'),
        unique_users=Sum('unique_users'),
        avg_satisfaction=Avg('satisfaction_score'),
    )

    # Recent conversations
    recent_conversations = Conversation.objects.filter(
        organization=organization
    ).select_related('user', 'ai_agent').order_by('-last_message_at')[:10]

    # Recent notifications
    notifications = Notification.objects.filter(
        recipient=user,
        is_read=False
    ).order_by('-created_at')[:5]

    # System alerts
    system_alerts = LogEntry.objects.filter(
        Q(organization=organization) | Q(organization__isnull=True),
        level__in=['error', 'critical'],
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-timestamp')[:5]

    # Get all agents for this organization
    agents = AIAgent.objects.filter(organization=organization)
    active_agents = agents.filter(status='active').count()

    # Get conversations for the user
    conversations = Conversation.objects.filter(user=user).order_by('-last_message_at')

    # Calculate average rating for user's conversations
    avg_rating = Feedback.objects.filter(
        conversation__user=user
    ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

    # Get total messages count
    total_messages = Message.objects.filter(
        conversation__user=user
    ).count()

    context = {
        'analytics': analytics_data,
        'recent_conversations': recent_conversations,
        'notifications': notifications,
        'system_alerts': system_alerts,
        'agents': agents,
        'active_agents': active_agents,
        'conversations': conversations,
        'avg_rating': avg_rating,
        'total_messages': total_messages,
        'organization': organization,
    }

    return render(request, 'dashboard/home.html', context)

@login_required
def chat_interface(request):
    """Chat interface for testing AI agents"""
    organization = request.user.organization

    context = {
        'organization': organization,
    }

    return render(request, 'chat/chat.html', context)

@login_required
def analytics_view(request):
    """Analytics dashboard"""
    organization = request.user.organization

    # Date range filter
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)

    # Analytics data
    analytics = Analytics.objects.filter(
        organization=organization,
        date__gte=start_date
    ).order_by('date')

    # Aggregate metrics
    total_metrics = analytics.aggregate(
        conversations=Sum('total_conversations'),
        messages=Sum('total_messages'),
        users=Sum('unique_users'),
        avg_satisfaction=Avg('satisfaction_score'),
    )

    # Daily breakdown for charts
    daily_data = list(analytics.values('date', 'total_conversations', 'total_messages', 'unique_users'))

    context = {
        'analytics': analytics,
        'total_metrics': total_metrics,
        'daily_data': daily_data,
        'days': days,
        'organization': organization,
    }

    return render(request, 'dashboard/analytics.html', context)

@login_required
def conversations_view(request):
    """Conversations log view"""
    organization = request.user.organization

    # Filters
    status = request.GET.get('status', '')
    ai_agent_id = request.GET.get('agent', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    conversations = Conversation.objects.filter(
        organization=organization
    ).select_related('user', 'ai_agent', 'transferred_to')

    if status:
        conversations = conversations.filter(status=status)
    if ai_agent_id:
        conversations = conversations.filter(ai_agent_id=ai_agent_id)
    if date_from:
        conversations = conversations.filter(started_at__date__gte=date_from)
    if date_to:
        conversations = conversations.filter(started_at__date__lte=date_to)

    conversations = conversations.order_by('-last_message_at')

    # Pagination would be added here in production

    ai_agents = AIAgent.objects.filter(organization=organization, status='active')

    context = {
        'conversations': conversations,
        'ai_agents': ai_agents,
        'filters': {
            'status': status,
            'agent': ai_agent_id,
            'date_from': date_from,
            'date_to': date_to,
        },
        'organization': organization,
    }

    return render(request, 'dashboard/conversations.html', context)

@login_required
def agent_management(request):
    """AI Agent management view"""
    organization = request.user.organization

    # Get all agents for this organization
    agents = AIAgent.objects.filter(organization=organization).order_by('-created_at')

    # Statistics
    total_agents = agents.count()
    active_agents = agents.filter(status='active').count()
    total_conversations = Conversation.objects.filter(
        organization=organization,
        ai_agent__isnull=False
    ).count()

    # Recent agent performance
    agent_performance = []
    for agent in agents[:10]:
        conv_count = Conversation.objects.filter(ai_agent=agent).count()
        avg_rating = Feedback.objects.filter(
            conversation__ai_agent=agent
        ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

        agent_performance.append({
            'agent': agent,
            'conversations': conv_count,
            'avg_rating': round(avg_rating, 1),
        })

    # Get conversations for the user
    conversations = Conversation.objects.filter(user=request.user).order_by('-last_message_at')

    # Calculate average rating for user's conversations
    avg_rating = Feedback.objects.filter(
        conversation__user=request.user
    ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

    context = {
        'agents': agents,
        'total_agents': total_agents,
        'active_agents': active_agents,
        'total_conversations': total_conversations,
        'agent_performance': agent_performance,
        'conversations': conversations,
        'avg_rating': avg_rating,
        'organization': organization,
    }

    return render(request, 'dashboard/agent_management.html', context)

@login_required
def system_settings(request):
    """System settings view"""
    organization = request.user.organization

    if request.method == 'POST':
        # Handle settings updates
        category = request.POST.get('category')
        key = request.POST.get('key')
        value = request.POST.get('value')

        setting, created = SystemSetting.objects.get_or_create(
            organization=organization,
            category=category,
            key=key,
            defaults={'value': value, 'description': f'{category} {key} setting'}
        )

        if not created:
            setting.value = value
            setting.save()

        messages.success(request, f"Setting '{key}' updated successfully.")
        return redirect('dashboard:system_settings')

    # Get current settings
    settings = SystemSetting.objects.filter(
        Q(organization=organization) | Q(organization__isnull=True),
        is_active=True
    ).order_by('category', 'key')

    # Group by category
    settings_by_category = {}
    for setting in settings:
        if setting.category not in settings_by_category:
            settings_by_category[setting.category] = []
        settings_by_category[setting.category].append(setting)

    context = {
        'settings_by_category': settings_by_category,
        'organization': organization,
    }

    return render(request, 'dashboard/system_settings.html', context)

@login_required
def intents_training(request):
    """Intents and training view"""
    organization = request.user.organization

    # Get all AI agents and their intents
    agents = AIAgent.objects.filter(organization=organization).prefetch_related('intents')

    context = {
        'agents': agents,
        'organization': organization,
    }

    return render(request, 'dashboard/intents_training.html', context)

@login_required
def review_ratings(request):
    """Review and ratings view"""
    organization = request.user.organization

    # Get feedback data
    feedback = Feedback.objects.filter(
        conversation__organization=organization
    ).select_related('conversation', 'user', 'conversation__ai_agent').order_by('-created_at')

    # Statistics
    total_feedback = feedback.count()
    avg_rating = feedback.aggregate(avg=Avg('rating'))['avg'] or 0
    rating_distribution = feedback.values('rating').annotate(count=Count('rating')).order_by('rating')

    # Recent feedback
    recent_feedback = feedback[:20]

    context = {
        'feedback': feedback,
        'total_feedback': total_feedback,
        'avg_rating': round(avg_rating, 1),
        'rating_distribution': list(rating_distribution),
        'recent_feedback': recent_feedback,
        'organization': organization,
    }

    return render(request, 'dashboard/review_ratings.html', context)

@login_required
def security_logs(request):
    """Security and logs view"""
    organization = request.user.organization

    # Get logs
    logs = LogEntry.objects.filter(
        Q(organization=organization) | Q(organization__isnull=True)
    ).select_related('user').order_by('-timestamp')

    # Filter options
    level = request.GET.get('level', '')
    category = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')

    if level:
        logs = logs.filter(level=level)
    if category:
        logs = logs.filter(category=category)
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)

    # Recent logs for display
    recent_logs = logs[:100]

    # Statistics
    log_stats = logs.values('level').annotate(count=Count('level')).order_by('level')

    context = {
        'logs': recent_logs,
        'log_stats': list(log_stats),
        'filters': {
            'level': level,
            'category': category,
            'date_from': date_from,
        },
        'organization': organization,
    }

    return render(request, 'dashboard/security_logs.html', context)