from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.db.models import Avg
from django.utils import timezone
from .models import User, Organization
from .forms import UserRegistrationForm, UserProfileForm
from core.models import Client, BanglaConversation, CallLog

def client_dashboard_view(request):
    """Client dashboard view for logged-in users"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    # Get user-specific statistics
    user_stats = {
        'user_conversations': BanglaConversation.objects.filter(user_name=request.user.username).count(),
        'user_voice_calls': CallLog.objects.filter(caller_name=request.user.username).count(),
        'average_rating': BanglaConversation.objects.filter(
            user_name=request.user.username,
            satisfaction_rating__isnull=False
        ).aggregate(avg_rating=Avg('satisfaction_rating'))['avg_rating'] or 0,
    }
    
    # Recent conversations for this user
    recent_conversations = BanglaConversation.objects.filter(
        user_name=request.user.username
    ).order_by('-created_at')[:10]
    
    context = {
        'user_stats': user_stats,
        'recent_conversations': recent_conversations,
        'user': request.user,
        'is_client_dashboard': True,
    }
    
    return render(request, 'accounts/client_dashboard.html', context)

def public_dashboard_view(request):
    """Public dashboard view showing platform statistics and features"""
    # Get public statistics
    stats = {
        'total_users': User.objects.count(),
        'total_conversations': BanglaConversation.objects.count(),
        'total_voice_calls': CallLog.objects.count(),
        'total_clients': Client.objects.filter(is_active=True).count(),
        'active_conversations': BanglaConversation.objects.filter(status='active').count(),
        'average_rating': BanglaConversation.objects.filter(satisfaction_rating__isnull=False).aggregate(
            avg_rating=Avg('satisfaction_rating')
        )['avg_rating'] or 0,
    }
    
    # Recent activity (public)
    recent_stats = {
        'conversations_today': BanglaConversation.objects.filter(
            created_at__date=timezone.now().date()
        ).count(),
        'voice_calls_today': CallLog.objects.filter(
            timestamp__date=timezone.now().date()
        ).count(),
    }
    
    context = {
        'stats': stats,
        'recent_stats': recent_stats,
        'is_public': True,
    }
    
    return render(request, 'accounts/public_dashboard.html', context)

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('bangla_admin_dashboard')
        else:
            return redirect('accounts:client_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                next_url = request.GET.get('next', 'bangla_admin_dashboard')
            else:
                next_url = request.GET.get('next', 'accounts:client_dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:public_dashboard')

def register_view(request):
    """User registration view with organization approval"""
    if request.user.is_authenticated:
        return redirect('accounts:public_dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create organization if provided
            org_name = request.POST.get('organization_name')
            if org_name:
                organization = Organization.objects.create(
                    name=org_name,
                    contact_email=user.email,
                    contact_phone=user.phone,
                    approval_status='pending'
                )
                user.organization = organization
                user.save()
                
                messages.success(request, 'Registration successful! Your organization is pending admin approval. You will receive an email once approved.')
            else:
                messages.success(request, 'Registration successful! Welcome to BanglaChatPro.')
            
            login(request, user)
            return redirect('accounts:client_dashboard')
        # If form is invalid, it will fall through to the render below with errors
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    # Add password change form
    password_form = PasswordChangeForm(request.user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'password_form': password_form
    })

@login_required
def password_change_view(request):
    """Password change view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form': form})