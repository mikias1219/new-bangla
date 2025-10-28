from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
import json

from core.models import Client, BanglaConversation, CallLog, BanglaIntent
from services.openai_service import openai_service


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_send(request):
    """
    Send a message and get AI response
    POST /api/chat/
    """
    data = request.data
    
    # Extract required fields
    client_id = data.get('client_id')
    user_name = data.get('user_name')
    message = data.get('message')
    
    if not all([client_id, user_name, message]):
        return Response(
            {'error': 'Missing required fields: client_id, user_name, message'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        client = Client.objects.get(id=client_id, is_active=True)
    except Client.DoesNotExist:
        return Response(
            {'error': 'Client not found or inactive'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
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
    
    # Generate AI response
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
    
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voice_process(request):
    """
    Process voice input and return audio response
    POST /api/voice/
    """
    data = request.data
    
    # Extract required fields
    client_id = data.get('client_id')
    caller_name = data.get('caller_name')
    question = data.get('question')
    
    if not all([client_id, caller_name, question]):
        return Response(
            {'error': 'Missing required fields: client_id, caller_name, question'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        client = Client.objects.get(id=client_id, is_active=True)
    except Client.DoesNotExist:
        return Response(
            {'error': 'Client not found or inactive'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
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
        voice="alloy",  # You can make this configurable
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
    
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_conversation(request):
    """
    Rate a conversation
    POST /api/rate/
    """
    data = request.data
    
    conversation_id = data.get('conversation_id')
    rating = data.get('rating')
    
    if not all([conversation_id, rating]):
        return Response(
            {'error': 'Missing required fields: conversation_id, rating'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        conversation = BanglaConversation.objects.get(id=conversation_id)
    except BanglaConversation.DoesNotExist:
        return Response(
            {'error': 'Conversation not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    conversation.satisfaction_rating = rating
    conversation.save()
    
    return Response({
        'message': 'Rating saved successfully',
        'conversation_id': conversation.id,
        'rating': rating
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_human_handoff(request):
    """
    Request human handoff
    POST /api/handoff/
    """
    data = request.data
    
    conversation_id = data.get('conversation_id')
    reason = data.get('reason', 'User requested human help')
    
    if not conversation_id:
        return Response(
            {'error': 'Missing required field: conversation_id'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        conversation = BanglaConversation.objects.get(id=conversation_id)
    except BanglaConversation.DoesNotExist:
        return Response(
            {'error': 'Conversation not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    conversation.is_escalated = True
    conversation.escalated_at = timezone.now()
    conversation.status = 'escalated'
    conversation.save()
    
    return Response({
        'message': 'Human handoff requested successfully',
        'conversation_id': conversation.id,
        'escalated_at': conversation.escalated_at.isoformat()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_status(request, order_id):
    """
    Get mock order status
    GET /api/orders/<id>/
    """
    # Mock order data
    mock_orders = {
        '1': {
            'order_id': '1',
            'status': 'প্রক্রিয়াধীন',
            'tracking_number': 'TRK123456',
            'estimated_delivery': '2024-01-15',
            'items': ['পণ্য ১', 'পণ্য ২']
        },
        '2': {
            'order_id': '2',
            'status': 'ডেলিভারি হয়েছে',
            'tracking_number': 'TRK789012',
            'delivered_at': '2024-01-10',
            'items': ['পণ্য ৩']
        }
    }
    
    order_data = mock_orders.get(str(order_id))
    if not order_data:
        return Response(
            {'error': 'Order not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(order_data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_clients(request):
    """
    Manage clients
    GET/POST /api/clients/
    """
    if request.method == 'GET':
        clients = Client.objects.filter(is_active=True)
        client_data = []
        for client in clients:
            client_data.append({
                'id': client.id,
                'name': client.name,
                'domain': client.domain,
                'contact_email': client.contact_email,
                'is_active': client.is_active
            })
        return Response(client_data)
    
    elif request.method == 'POST':
        data = request.data
        
        required_fields = ['name', 'domain', 'contact_email']
        if not all(field in data for field in required_fields):
            return Response(
                {'error': f'Missing required fields: {required_fields}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        client = Client.objects.create(
            name=data['name'],
            domain=data['domain'],
            contact_email=data['contact_email'],
            description=data.get('description', ''),
            website=data.get('website', ''),
            phone=data.get('phone', '')
        )
        
        return Response({
            'id': client.id,
            'name': client.name,
            'domain': client.domain,
            'contact_email': client.contact_email,
            'message': 'Client created successfully'
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_intents(request):
    """
    Manage intents
    GET/POST /api/intents/
    """
    if request.method == 'GET':
        client_id = request.GET.get('client_id')
        if not client_id:
            return Response(
                {'error': 'client_id parameter required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        intents = BanglaIntent.objects.filter(client=client, is_active=True)
        intent_data = []
        for intent in intents:
            intent_data.append({
                'id': intent.id,
                'name': intent.name,
                'training_phrase': intent.training_phrase,
                'ai_response_template': intent.ai_response_template,
                'usage_count': intent.usage_count,
                'success_rate': intent.success_rate
            })
        return Response(intent_data)
    
    elif request.method == 'POST':
        data = request.data
        
        required_fields = ['client_id', 'name', 'training_phrase', 'ai_response_template']
        if not all(field in data for field in required_fields):
            return Response(
                {'error': f'Missing required fields: {required_fields}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = Client.objects.get(id=data['client_id'])
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        intent = BanglaIntent.objects.create(
            client=client,
            name=data['name'],
            training_phrase=data['training_phrase'],
            ai_response_template=data['ai_response_template'],
            description=data.get('description', ''),
            examples=data.get('examples', []),
            responses=data.get('responses', [])
        )
        
        return Response({
            'id': intent.id,
            'name': intent.name,
            'training_phrase': intent.training_phrase,
            'ai_response_template': intent.ai_response_template,
            'message': 'Intent created successfully'
        }, status=status.HTTP_201_CREATED)