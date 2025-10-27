from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Conversation, Message, AIAgent, Intent, Feedback
import json

@login_required
def chat_interface(request):
    """Chat interface view"""
    # Get or create conversation
    conversation_id = request.GET.get('conversation')
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    else:
        # Create new conversation
        conversation = Conversation.objects.create(
            user=request.user,
            organization=request.user.organization
        )

    # Get conversation history
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')

    # Get user's conversations
    conversations = Conversation.objects.filter(user=request.user).order_by('-last_message_at')[:10]

    context = {
        'conversation': conversation,
        'messages': messages,
        'conversations': conversations,
    }

    return render(request, 'chat/chat.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """Conversation detail view"""
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')

    context = {
        'conversation': conversation,
        'messages': messages,
    }

    return render(request, 'chat/conversation_detail.html', context)

@login_required
def start_conversation(request):
    """Start a new conversation"""
    conversation = Conversation.objects.create(
        user=request.user,
        organization=request.user.organization
    )

    return JsonResponse({
        'success': True,
        'conversation_id': conversation.id,
        'redirect_url': f'/chat/?conversation={conversation.id}'
    })

@login_required
@csrf_exempt
def send_message(request):
    """Send a message in conversation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            conversation_id = data.get('conversation_id')
            content = data.get('content')

            if not conversation_id or not content:
                return JsonResponse({'error': 'Conversation ID and content are required'}, status=400)

            conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)

            # Create user message
            message = Message.objects.create(
                conversation=conversation,
                sender_type='user',
                sender=request.user,
                content=content
            )

            # Update conversation stats
            conversation.message_count += 1
            conversation.last_message_at = timezone.now()
            conversation.save()

            # Simulate AI response (in production, this would call your AI service)
            ai_response = generate_ai_response(content, conversation)

            ai_message = Message.objects.create(
                conversation=conversation,
                sender_type='ai',
                content=ai_response,
                confidence_score=0.85
            )

            conversation.message_count += 1
            conversation.ai_responses += 1
            conversation.save()

            return JsonResponse({
                'success': True,
                'user_message': {
                    'id': message.id,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat()
                },
                'ai_message': {
                    'id': ai_message.id,
                    'content': ai_message.content,
                    'timestamp': ai_message.timestamp.isoformat(),
                    'confidence': ai_message.confidence_score
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def transfer_conversation(request, conversation_id):
    """Transfer conversation to human agent"""
    if request.method == 'POST':
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)

        # Mark as transferred
        conversation.status = 'transferred'
        conversation.transferred_to = request.user  # In production, assign to available agent
        conversation.transfer_reason = request.POST.get('reason', 'User requested human assistance')
        conversation.save()

        messages.success(request, 'Conversation has been transferred to a human agent.')

    return redirect('chat:interface')

@login_required
def submit_feedback(request, conversation_id):
    """Submit feedback for conversation"""
    if request.method == 'POST':
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)

        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')

        if rating:
            Feedback.objects.create(
                conversation=conversation,
                user=request.user,
                rating=int(rating),
                comment=comment
            )
            messages.success(request, 'Thank you for your feedback!')

    return redirect('chat:conversation_detail', conversation_id=conversation_id)

def generate_ai_response(user_message, conversation):
    """Generate AI response (mock implementation)"""
    # This is a simple mock response generator
    # In production, this would integrate with your AI service

    responses = [
        "I understand your concern. Let me help you with that.",
        "That's an interesting question. Here's what I can tell you:",
        "Thank you for reaching out. Based on what you've shared:",
        "I see you need assistance with this. Let me provide some guidance:",
        "That's a great question! Here's my response:",
    ]

    # Simple keyword-based responses
    if 'hello' in user_message.lower() or 'hi' in user_message.lower():
        return "Hello! How can I assist you today?"
    elif 'help' in user_message.lower():
        return "I'm here to help! What specific assistance do you need?"
    elif 'bye' in user_message.lower() or 'goodbye' in user_message.lower():
        return "Goodbye! If you need help again, feel free to start a new conversation."
    elif 'thank' in user_message.lower():
        return "You're welcome! Is there anything else I can help you with?"
    else:
        # Return a random response
        import random
        return random.choice(responses) + f" Regarding '{user_message[:50]}...', I can provide more detailed assistance."