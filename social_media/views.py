from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import models
from .models import SocialMediaAccount, SocialMediaMessage, SocialMediaWebhook, SocialMediaAutoReply, SocialMediaAnalytics
from services.social_media_service import SocialMediaService


@login_required
@xframe_options_exempt
def social_accounts_list(request):
    """List all social media accounts for the organization"""
    organization = request.user.organization
    accounts = SocialMediaAccount.objects.filter(organization=organization).order_by('-created_at')
    
    # Get recent messages (last 10)
    recent_messages = SocialMediaMessage.objects.filter(
        organization=organization
    ).select_related('social_account').order_by('-received_at')[:10]

    context = {
        'accounts': accounts,
        'recent_messages': recent_messages,
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
            verify_token = request.POST.get('verify_token') or f"fb_{organization.id}_{hash(page_id) % 10000}"

            try:
                social_service = SocialMediaService(organization)
                account = social_service.connect_facebook(page_id, access_token, page_name)
                
                # Save webhook secret for verification
                account.webhook_secret = verify_token
                account.webhook_url = request.build_absolute_uri(f'/social/webhook/facebook/{organization.id}/')
                account.save()
                
                # Optionally assign AI agent
                ai_agent_id = request.POST.get('ai_agent_id')
                if ai_agent_id:
                    from chat.models import AIAgent
                    try:
                        ai_agent = AIAgent.objects.get(id=ai_agent_id, organization=organization)
                        account.ai_agent = ai_agent
                        account.save()
                    except AIAgent.DoesNotExist:
                        pass
                
                messages.success(request, f'Successfully connected Facebook page: {page_name}. Webhook URL: {account.webhook_url}')
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
                
                # Optionally assign AI agent
                ai_agent_id = request.POST.get('ai_agent_id')
                if ai_agent_id:
                    from chat.models import AIAgent
                    try:
                        ai_agent = AIAgent.objects.get(id=ai_agent_id, organization=organization)
                        account.ai_agent = ai_agent
                        account.save()
                    except AIAgent.DoesNotExist:
                        pass
                
                messages.success(request, f'Successfully connected Twitter account: {account_name}')
                return redirect('social_media:accounts_list')
            except Exception as e:
                messages.error(request, f'Failed to connect Twitter account: {str(e)}')

        elif platform == 'instagram':
            account_id = request.POST.get('account_id')
            access_token = request.POST.get('access_token')
            account_name = request.POST.get('account_name')
            verify_token = request.POST.get('verify_token') or f"ig_{organization.id}_{hash(account_id) % 10000}"

            try:
                social_service = SocialMediaService(organization)
                account = social_service.connect_instagram(account_id, access_token, account_name)
                
                # Save webhook secret and URL
                account.webhook_secret = verify_token
                account.webhook_url = request.build_absolute_uri(f'/social/webhook/instagram/{organization.id}/')
                account.save()
                
                # Optionally assign AI agent
                ai_agent_id = request.POST.get('ai_agent_id')
                if ai_agent_id:
                    from chat.models import AIAgent
                    try:
                        ai_agent = AIAgent.objects.get(id=ai_agent_id, organization=organization)
                        account.ai_agent = ai_agent
                        account.save()
                    except AIAgent.DoesNotExist:
                        pass
                
                messages.success(request, f'Successfully connected Instagram account: {account_name}. Webhook URL: {account.webhook_url}')
                return redirect('social_media:accounts_list')
            except Exception as e:
                messages.error(request, f'Failed to connect Instagram account: {str(e)}')

        elif platform == 'whatsapp':
            phone_number_id = request.POST.get('phone_number_id')
            access_token = request.POST.get('access_token')
            account_name = request.POST.get('account_name')
            verify_token = request.POST.get('verify_token') or f"wa_{organization.id}_{hash(phone_number_id) % 10000}"

            try:
                social_service = SocialMediaService(organization)
                account = social_service.connect_whatsapp(phone_number_id, access_token, account_name, verify_token)
                
                # Save webhook URL
                account.webhook_url = request.build_absolute_uri(f'/social/webhook/whatsapp/{organization.id}/')
                account.save()
                
                # Optionally assign AI agent
                ai_agent_id = request.POST.get('ai_agent_id')
                if ai_agent_id:
                    from chat.models import AIAgent
                    try:
                        ai_agent = AIAgent.objects.get(id=ai_agent_id, organization=organization)
                        account.ai_agent = ai_agent
                        account.save()
                    except AIAgent.DoesNotExist:
                        pass
                
                messages.success(request, f'Successfully connected WhatsApp account: {account_name}. Webhook URL: {account.webhook_url}. Verify Token: {verify_token}')
                return redirect('social_media:accounts_list')
            except Exception as e:
                messages.error(request, f'Failed to connect WhatsApp account: {str(e)}')

    # Get available AI agents for this organization
    from chat.models import AIAgent
    ai_agents = AIAgent.objects.filter(organization=organization, status='active')

    context = {
        'platform': platform,
        'ai_agents': ai_agents,
    }

    return render(request, 'social_media/connect_account.html', context)


@login_required
def account_detail(request, account_id):
    """View social media account details including webhook URL"""
    organization = request.user.organization
    account = get_object_or_404(SocialMediaAccount, id=account_id, organization=organization)

    # Get account statistics (if method exists)
    try:
        social_service = SocialMediaService(organization)
        stats = social_service.get_account_stats(account) if hasattr(social_service, 'get_account_stats') else {}
    except Exception:
        stats = {}

    # Recent messages
    recent_messages = SocialMediaMessage.objects.filter(
        social_account=account
    ).order_by('-received_at')[:20]

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
def facebook_webhook(request, organization_id):
    """Handle Facebook webhooks with proper verification"""
    import json
    import hashlib
    import hmac
    
    try:
        from accounts.models import Organization
        organization = Organization.objects.get(id=organization_id)

        # Handle Facebook webhook verification (GET request)
        if request.method == 'GET':
            mode = request.GET.get('hub.mode')
            verify_token = request.GET.get('hub.verify_token')
            challenge = request.GET.get('hub.challenge')

            if mode != 'subscribe':
                return HttpResponse('Invalid mode', status=400)

            # Get verification token from any Facebook account for this organization
            from .models import SocialMediaAccount
            facebook_account = SocialMediaAccount.objects.filter(
                organization=organization,
                platform='facebook',
                is_active=True
            ).first()

            if facebook_account and facebook_account.webhook_secret == verify_token:
                return HttpResponse(challenge, content_type='text/plain')
            else:
                return HttpResponse('Verification failed', status=403)

        # Handle webhook data (POST request)
        if request.method == 'POST':
            # Verify webhook signature (optional but recommended)
            signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')
            if signature:
                from django.conf import settings
                app_secret = getattr(settings, 'FACEBOOK_APP_SECRET', '')
                if app_secret:
                    expected_signature = 'sha256=' + hmac.new(
                        app_secret.encode('utf-8'),
                        request.body,
                        hashlib.sha256
                    ).hexdigest()
                    if not hmac.compare_digest(signature, expected_signature):
                        return HttpResponse('Invalid signature', status=403)

            # Parse JSON data
            try:
                data = json.loads(request.body) if request.body else {}
            except json.JSONDecodeError:
                return HttpResponse('Invalid JSON', status=400)

            # Process webhook
            social_service = SocialMediaService(organization)
            social_service.handle_facebook_webhook(data)

            return HttpResponse('OK', content_type='text/plain')

        return HttpResponse('Method not allowed', status=405)

    except Organization.DoesNotExist:
        return HttpResponse('Organization not found', status=404)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Facebook webhook error: {e}", exc_info=True)
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
def instagram_webhook(request, organization_id):
    """Handle Instagram webhooks (uses Facebook Graph API)"""
    import json
    import hashlib
    import hmac
    
    try:
        from accounts.models import Organization
        organization = Organization.objects.get(id=organization_id)

        # Handle Instagram webhook verification (GET request)
        if request.method == 'GET':
            mode = request.GET.get('hub.mode')
            verify_token = request.GET.get('hub.verify_token')
            challenge = request.GET.get('hub.challenge')

            if mode != 'subscribe':
                return HttpResponse('Invalid mode', status=400)

            # Get verification token from Instagram account
            from .models import SocialMediaAccount
            instagram_account = SocialMediaAccount.objects.filter(
                organization=organization,
                platform='instagram',
                is_active=True
            ).first()

            if instagram_account and instagram_account.webhook_secret == verify_token:
                return HttpResponse(challenge, content_type='text/plain')
            else:
                return HttpResponse('Verification failed', status=403)

        # Handle webhook data (POST request)
        if request.method == 'POST':
            # Verify webhook signature
            signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')
            if signature:
                from django.conf import settings
                app_secret = getattr(settings, 'FACEBOOK_APP_SECRET', '')
                if app_secret:
                    expected_signature = 'sha256=' + hmac.new(
                        app_secret.encode('utf-8'),
                        request.body,
                        hashlib.sha256
                    ).hexdigest()
                    if not hmac.compare_digest(signature, expected_signature):
                        return HttpResponse('Invalid signature', status=403)

            # Parse JSON data
            try:
                data = json.loads(request.body) if request.body else {}
            except json.JSONDecodeError:
                return HttpResponse('Invalid JSON', status=400)

            # Process webhook (Instagram uses same structure as Facebook)
            social_service = SocialMediaService(organization)
            social_service.handle_instagram_webhook(data)

            return HttpResponse('OK', content_type='text/plain')

        return HttpResponse('Method not allowed', status=405)

    except Organization.DoesNotExist:
        return HttpResponse('Organization not found', status=404)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Instagram webhook error: {e}", exc_info=True)
        return HttpResponse('Error', status=500)

@csrf_exempt
def whatsapp_webhook(request, organization_id):
    """Handle WhatsApp Business API webhooks with proper verification"""
    import json
    import hashlib
    import hmac
    
    try:
        from accounts.models import Organization
        organization = Organization.objects.get(id=organization_id)

        # Handle webhook verification (GET request)
        if request.method == 'GET':
            mode = request.GET.get('hub.mode')
            token = request.GET.get('hub.verify_token')
            challenge = request.GET.get('hub.challenge')

            if mode != 'subscribe':
                return HttpResponse('Invalid mode', status=400)

            # Get the verify token from WhatsApp account
            from .models import SocialMediaAccount
            whatsapp_account = SocialMediaAccount.objects.filter(
                organization=organization,
                platform='whatsapp',
                is_active=True
            ).first()

            if whatsapp_account and whatsapp_account.webhook_secret == token:
                return HttpResponse(challenge, content_type='text/plain')
            else:
                return HttpResponse('Verification failed', status=403)

        # Handle webhook data (POST request)
        if request.method == 'POST':
            # Verify webhook signature
            signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')
            if signature:
                from django.conf import settings
                app_secret = getattr(settings, 'WHATSAPP_APP_SECRET', '')
                if not app_secret:
                    # Fallback to access token for verification
                    whatsapp_account = SocialMediaAccount.objects.filter(
                        organization=organization,
                        platform='whatsapp',
                        is_active=True
                    ).first()
                    if whatsapp_account:
                        app_secret = whatsapp_account.access_token[:32]  # Use first 32 chars
                
                if app_secret:
                    expected_signature = 'sha256=' + hmac.new(
                        app_secret.encode('utf-8'),
                        request.body,
                        hashlib.sha256
                    ).hexdigest()
                    if not hmac.compare_digest(signature, expected_signature):
                        return HttpResponse('Invalid signature', status=403)

            # Parse JSON data
            try:
                data = json.loads(request.body) if request.body else {}
            except json.JSONDecodeError:
                return HttpResponse('Invalid JSON', status=400)

            # Process webhook
            social_service = SocialMediaService(organization)
            social_service.handle_whatsapp_webhook(data)

            return HttpResponse('OK', content_type='text/plain')

        return HttpResponse('Method not allowed', status=405)

    except Organization.DoesNotExist:
        return HttpResponse('Organization not found', status=404)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"WhatsApp webhook error: {e}", exc_info=True)
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