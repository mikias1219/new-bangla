from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import models
from .models import SocialMediaAccount, SocialMediaMessage, SocialMediaWebhook, SocialMediaAutoReply, SocialMediaAnalytics
from services.social_media_service import SocialMediaService


@login_required
def social_accounts_list(request):
    """List all social media accounts for the organization"""
    organization = request.user.organization
    accounts = SocialMediaAccount.objects.filter(organization=organization)

    context = {
        'accounts': accounts,
    }

    return render(request, 'social_media/accounts_list.html', context)


@login_required
def connect_account(request, platform):
    """Connect a social media account"""
    organization = request.user.organization

    if request.method == 'POST':
        if platform == 'facebook':
            page_id = request.POST.get('page_id')
            access_token = request.POST.get('access_token')
            page_name = request.POST.get('page_name')

            try:
                social_service = SocialMediaService(organization)
                account = social_service.connect_facebook(page_id, access_token, page_name)
                messages.success(request, f'Successfully connected Facebook page: {page_name}')
                return redirect('social_media:accounts_list')
            except Exception as e:
                messages.error(request, f'Failed to connect Facebook page: {str(e)}')

        elif platform == 'twitter':
            account_id = request.POST.get('account_id')
            access_token = request.POST.get('access_token')
            access_token_secret = request.POST.get('access_token_secret')
            account_name = request.POST.get('account_name')

            try:
                social_service = SocialMediaService(organization)
                account = social_service.connect_twitter(account_id, access_token, access_token_secret, account_name)
                messages.success(request, f'Successfully connected Twitter account: {account_name}')
                return redirect('social_media:accounts_list')
            except Exception as e:
                messages.error(request, f'Failed to connect Twitter account: {str(e)}')

        elif platform == 'instagram':
            account_id = request.POST.get('account_id')
            access_token = request.POST.get('access_token')
            account_name = request.POST.get('account_name')

            try:
                social_service = SocialMediaService(organization)
                account = social_service.connect_instagram(account_id, access_token, account_name)
                messages.success(request, f'Successfully connected Instagram account: {account_name}')
                return redirect('social_media:accounts_list')
            except Exception as e:
                messages.error(request, f'Failed to connect Instagram account: {str(e)}')

    context = {
        'platform': platform,
    }

    return render(request, 'social_media/connect_account.html', context)


@login_required
def account_detail(request, account_id):
    """View social media account details and analytics"""
    organization = request.user.organization
    account = get_object_or_404(SocialMediaAccount, id=account_id, organization=organization)

    # Get account statistics
    social_service = SocialMediaService(organization)
    stats = social_service.get_account_stats(account)

    # Recent messages
    recent_messages = SocialMediaMessage.objects.filter(
        social_account=account
    ).order_by('-received_at')[:10]

    context = {
        'account': account,
        'stats': stats,
        'recent_messages': recent_messages,
    }

    return render(request, 'social_media/account_detail.html', context)


@login_required
def disconnect_account(request, account_id):
    """Disconnect a social media account"""
    organization = request.user.organization
    account = get_object_or_404(SocialMediaAccount, id=account_id, organization=organization)

    if request.method == 'POST':
        account.is_active = False
        account.save()
        messages.success(request, f'Successfully disconnected {account.platform} account: {account.account_name}')

    return redirect('social_media:accounts_list')


@login_required
def messages_list(request):
    """List all social media messages"""
    organization = request.user.organization

    # Filter parameters
    platform = request.GET.get('platform')
    account_id = request.GET.get('account')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    messages_query = SocialMediaMessage.objects.filter(organization=organization)

    if platform:
        messages_query = messages_query.filter(social_account__platform=platform)
    if account_id:
        messages_query = messages_query.filter(social_account_id=account_id)

    if date_from:
        messages_query = messages_query.filter(received_at__date__gte=date_from)
    if date_to:
        messages_query = messages_query.filter(received_at__date__lte=date_to)

    messages_list = messages_query.order_by('-received_at')[:100]  # Limit to recent 100

    # Get accounts for filter dropdown
    accounts = SocialMediaAccount.objects.filter(organization=organization, is_active=True)

    context = {
        'messages': messages_list,
        'accounts': accounts,
        'selected_platform': platform,
        'selected_account': account_id,
    }

    return render(request, 'social_media/messages_list.html', context)


@login_required
def message_detail(request, message_id):
    """View detailed message information"""
    organization = request.user.organization
    message = get_object_or_404(SocialMediaMessage, id=message_id, organization=organization)

    context = {
        'message': message,
    }

    return render(request, 'social_media/message_detail.html', context)


# Webhook endpoints (no authentication required)
@csrf_exempt
@require_POST
def facebook_webhook(request, organization_id):
    """Handle Facebook webhooks"""
    try:
        from accounts.models import Organization
        organization = Organization.objects.get(id=organization_id)

        # Handle Facebook verification
        if request.method == 'GET':
            verify_token = request.GET.get('hub.verify_token')
            challenge = request.GET.get('hub.challenge')

            # In production, verify the token properly
            if verify_token == f"fb_verify_{organization_id}":
                return HttpResponse(challenge)
            else:
                return HttpResponse('Verification failed', status=403)

        # Handle webhook data
        social_service = SocialMediaService(organization)
        social_service.handle_facebook_webhook(request.POST)

        return HttpResponse('OK')

    except Exception as e:
        print(f"Facebook webhook error: {e}")
        return HttpResponse('Error', status=500)


@csrf_exempt
@require_POST
def twitter_webhook(request, organization_id):
    """Handle Twitter webhooks"""
    try:
        from accounts.models import Organization
        organization = Organization.objects.get(id=organization_id)

        social_service = SocialMediaService(organization)
        social_service.handle_twitter_webhook(request.POST)

        return HttpResponse('OK')

    except Exception as e:
        print(f"Twitter webhook error: {e}")
        return HttpResponse('Error', status=500)


@csrf_exempt
@require_POST
def instagram_webhook(request, organization_id):
    """Handle Instagram webhooks"""
    try:
        from accounts.models import Organization
        organization = Organization.objects.get(id=organization_id)

        # Instagram webhooks are similar to Facebook
        social_service = SocialMediaService(organization)
        social_service.handle_facebook_webhook(request.POST)  # Reuse Facebook handler

        return HttpResponse('OK')

    except Exception as e:
        print(f"Instagram webhook error: {e}")
        return HttpResponse('Error', status=500)


@login_required
def auto_replies_list(request):
    """List auto-replies for social media"""
    organization = request.user.organization
    auto_replies = SocialMediaAutoReply.objects.filter(
        social_account__organization=organization
    ).select_related('social_account').order_by('-created_at')

    context = {
        'auto_replies': auto_replies,
    }

    return render(request, 'social_media/auto_replies_list.html', context)


@login_required
def create_auto_reply(request):
    """Create a new auto-reply"""
    organization = request.user.organization
    accounts = SocialMediaAccount.objects.filter(organization=organization, is_active=True)

    if request.method == 'POST':
        social_account_id = request.POST.get('social_account')
        trigger_keywords = request.POST.get('trigger_keywords')
        response_text = request.POST.get('response_text')

        try:
            account = SocialMediaAccount.objects.get(id=social_account_id, organization=organization)

            auto_reply = SocialMediaAutoReply.objects.create(
                social_account=account,
                trigger_keywords=trigger_keywords.split(',') if trigger_keywords else [],
                response_text=response_text,
                trigger_type=request.POST.get('trigger_type', 'keyword'),
                priority=int(request.POST.get('priority', 0)),
            )

            messages.success(request, 'Auto-reply created successfully!')
            return redirect('social_media:auto_replies_list')

        except Exception as e:
            messages.error(request, f'Failed to create auto-reply: {str(e)}')

    context = {
        'accounts': accounts,
    }

    return render(request, 'social_media/create_auto_reply.html', context)


@login_required
def edit_auto_reply(request, reply_id):
    """Edit an existing auto-reply"""
    organization = request.user.organization
    auto_reply = get_object_or_404(
        SocialMediaAutoReply,
        id=reply_id,
        social_account__organization=organization
    )
    accounts = SocialMediaAccount.objects.filter(organization=organization, is_active=True)

    if request.method == 'POST':
        auto_reply.trigger_keywords = request.POST.get('trigger_keywords', '').split(',')
        auto_reply.response_text = request.POST.get('response_text')
        auto_reply.trigger_type = request.POST.get('trigger_type', 'keyword')
        auto_reply.priority = int(request.POST.get('priority', 0))
        auto_reply.is_active = request.POST.get('is_active') == 'on'
        auto_reply.save()

        messages.success(request, 'Auto-reply updated successfully!')
        return redirect('social_media:auto_replies_list')

    context = {
        'auto_reply': auto_reply,
        'accounts': accounts,
    }

    return render(request, 'social_media/edit_auto_reply.html', context)


@login_required
def delete_auto_reply(request, reply_id):
    """Delete an auto-reply"""
    organization = request.user.organization
    auto_reply = get_object_or_404(
        SocialMediaAutoReply,
        id=reply_id,
        social_account__organization=organization
    )

    if request.method == 'POST':
        auto_reply.delete()
        messages.success(request, 'Auto-reply deleted successfully!')

    return redirect('social_media:auto_replies_list')


@login_required
def analytics_dashboard(request):
    """Social media analytics dashboard"""
    organization = request.user.organization

    # Date range
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timezone.timedelta(days=days)

    # Get analytics data
    analytics_data = SocialMediaAnalytics.objects.filter(
        social_account__organization=organization,
        date__gte=start_date
    ).select_related('social_account').order_by('-date')

    # Aggregate statistics
    total_messages = analytics_data.aggregate(
        total_received=models.Sum('messages_received'),
        total_sent=models.Sum('messages_sent'),
        total_ai_responses=models.Sum('ai_responses')
    )

    # Platform breakdown
    platform_stats = {}
    for analytic in analytics_data:
        platform = analytic.social_account.platform
        if platform not in platform_stats:
            platform_stats[platform] = {
                'messages_received': 0,
                'messages_sent': 0,
                'ai_responses': 0,
            }
        platform_stats[platform]['messages_received'] += analytic.messages_received
        platform_stats[platform]['messages_sent'] += analytic.messages_sent
        platform_stats[platform]['ai_responses'] += analytic.ai_responses

    context = {
        'analytics_data': analytics_data[:50],  # Limit for display
        'total_stats': total_messages,
        'platform_stats': platform_stats,
        'days': days,
    }

    return render(request, 'social_media/analytics.html', context)


@login_required
def export_analytics(request):
    """Export social media analytics data"""
    # This would implement CSV/Excel export functionality
    # For now, just redirect back
    messages.info(request, 'Analytics export feature coming soon!')
    return redirect('social_media:analytics')