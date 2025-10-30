from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json

from core.models import Client, BanglaConversation, CallLog, BanglaIntent, Product
from services.openai_service import openai_service
from accounts.models import Organization
from rest_framework.decorators import permission_classes
from django.contrib.auth.decorators import login_required


@api_view(['POST'])
@authentication_classes([])  # No authentication required
@permission_classes([AllowAny])  # Allow anonymous access for chat
def chat_send(request):
    """
    Send a message and get AI response
    POST /api/chat/
    Note: CSRF is exempt for API views in DRF by default
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
    # Gate by organization approval if available
    org: Organization | None = getattr(request.user, 'organization', None) if request.user and request.user.is_authenticated else None
    if org and org.approval_status != 'approved':
        return Response({'error': 'Organization not approved yet'}, status=status.HTTP_403_FORBIDDEN)
    
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
        system_prompt=None,  # Let the service detect language and set appropriate prompt
        client_name=client.name
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
    # Gate by organization approval
    org: Organization | None = getattr(request.user, 'organization', None) if request.user and request.user.is_authenticated else None
    if org and org.approval_status != 'approved':
        return Response({'error': 'Organization not approved yet'}, status=status.HTTP_403_FORBIDDEN)
    
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
    # Increment simple success metrics for detected intent if present
    if conversation.intent_detected:
        try:
            intent = BanglaIntent.objects.get(client=conversation.client, name=conversation.intent_detected)
            intent.usage_count = (intent.usage_count or 0) + 1
            # naive average update
            prev = (intent.success_rate or 0.0) * max(intent.usage_count - 1, 0)
            intent.success_rate = (prev + (1.0 if rating >= 4 else 0.0)) / float(intent.usage_count)
            intent.save()
        except BanglaIntent.DoesNotExist:
            pass
    
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_product_availability(request):
    """
    Check product availability by product_id or sku
    GET /api/products/availability?product_id=... or sku=...
    Replace mock with real ERP/DB call.
    """
    product_id = request.GET.get('product_id')
    sku = request.GET.get('sku')
    if not (product_id or sku):
        return Response({'error': 'product_id or sku is required'}, status=400)
    # Query real DB
    try:
        if sku:
            prod = Product.objects.get(sku=sku, is_active=True)
        else:
            prod = Product.objects.get(sku=f'SKU-{product_id}', is_active=True)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)
    return Response({
        'sku': prod.sku,
        'name': prod.name,
        'in_stock': prod.in_stock,
        'qty': prod.stock_qty,
        'price': str(prod.price),
        'currency': prod.currency,
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def products_crud(request):
    """List or create products for the user's organization."""
    org = getattr(request.user, 'organization', None)
    if request.method == 'GET':
        if request.user.is_superuser:
            qs = Product.objects.all()
        elif org:
            qs = Product.objects.filter(organization=org)
        else:
            return Response({'error': 'No organization associated with user'}, status=400)
        data = [{
            'id': p.id,
            'sku': p.sku,
            'name': p.name,
            'price': str(p.price),
            'currency': p.currency,
            'in_stock': p.in_stock,
            'qty': p.stock_qty,
            'client_id': p.client_id,
        } for p in qs]
        return Response(data)
    # POST create
    payload = request.data
    required = ['sku', 'name', 'price', 'client_id']
    if not all(k in payload for k in required):
        return Response({'error': f'Missing required fields: {required}'}, status=400)
    try:
        client = Client.objects.get(id=payload['client_id'])
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=404)
    prod = Product.objects.create(
        organization=(org or (client and getattr(client, 'organization', None))) if not request.user.is_superuser else (org or getattr(request.user, 'organization', None)),
        client=client,
        sku=payload['sku'],
        name=payload['name'],
        description=payload.get('description', ''),
        price=payload.get('price', 0),
        currency=payload.get('currency', 'BDT'),
        in_stock=payload.get('in_stock', True),
        stock_qty=payload.get('qty', 0),
        is_active=True,
    )
    return Response({'id': prod.id, 'sku': prod.sku, 'name': prod.name}, status=201)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, product_id):
    org = getattr(request.user, 'organization', None)
    if not org:
        return Response({'error': 'No organization associated with user'}, status=400)
    try:
        prod = Product.objects.get(id=product_id, organization=org)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)
    if request.method == 'GET':
        return Response({
            'id': prod.id,
            'sku': prod.sku,
            'name': prod.name,
            'description': prod.description,
            'price': str(prod.price),
            'currency': prod.currency,
            'in_stock': prod.in_stock,
            'qty': prod.stock_qty,
            'client_id': prod.client_id,
        })
    if request.method in ['PUT', 'PATCH']:
        data = request.data
        for field in ['name', 'description', 'currency']:
            if field in data:
                setattr(prod, field, data[field])
        if 'price' in data:
            prod.price = data['price']
        if 'in_stock' in data:
            prod.in_stock = data['in_stock']
        if 'qty' in data:
            prod.stock_qty = data['qty']
        prod.save()
        return Response({'message': 'Updated', 'id': prod.id})
    # DELETE
    prod.delete()
    return Response(status=204)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_status(request):
    """
    Get payment status by payment_id
    GET /api/payments/status?payment_id=...
    Replace mock with real payment gateway or DB call.
    """
    payment_id = request.GET.get('payment_id')
    if not payment_id:
        return Response({'error': 'payment_id is required'}, status=400)
    mock = {
        'PMT1': { 'status': 'completed', 'amount': 1200, 'currency': 'BDT' },
        'PMT2': { 'status': 'pending', 'amount': 850, 'currency': 'BDT' },
    }
    data = mock.get(payment_id)
    if not data:
        return Response({'error': 'Payment not found'}, status=404)
    return Response({ 'payment_id': payment_id, **data })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_client_feature_status(request):
    """Return feature flags for the current user/org for client UI gating."""
    org: Organization | None = getattr(request.user, 'organization', None)
    approval = getattr(org, 'approval_status', 'pending') if org else 'pending'
    is_approved = approval == 'approved'
    return Response({
        'is_approved': is_approved,
        'approval_status': approval,
        'is_chat_enabled': is_approved,
        'is_voice_enabled': is_approved,
    })


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


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def client_detail(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=404)
    if request.method == 'GET':
        return Response({
            'id': client.id,
            'name': client.name,
            'domain': client.domain,
            'contact_email': client.contact_email,
            'is_active': client.is_active,
            'website': client.website,
            'phone': client.phone,
            'description': client.description,
        })
    if request.method in ['PUT', 'PATCH']:
        data = request.data
        for field in ['name','domain','contact_email','website','phone','description']:
            if field in data:
                setattr(client, field, data[field])
        if 'is_active' in data:
            client.is_active = data['is_active']
        client.save()
        return Response({'message': 'Updated', 'id': client.id})
    client.delete()
    return Response(status=204)


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


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def intent_detail(request, intent_id):
    try:
        intent = BanglaIntent.objects.get(id=intent_id)
    except BanglaIntent.DoesNotExist:
        return Response({'error': 'Intent not found'}, status=404)
    if request.method == 'GET':
        return Response({
            'id': intent.id,
            'name': intent.name,
            'training_phrase': intent.training_phrase,
            'ai_response_template': intent.ai_response_template,
            'description': intent.description,
            'examples': intent.examples,
            'responses': intent.responses,
            'confidence_threshold': intent.confidence_threshold,
            'is_active': intent.is_active,
        })
    if request.method in ['PUT', 'PATCH']:
        data = request.data
        for field in ['name','training_phrase','ai_response_template','description','examples','responses']:
            if field in data:
                setattr(intent, field, data[field])
        if 'confidence_threshold' in data:
            intent.confidence_threshold = data['confidence_threshold']
        if 'is_active' in data:
            intent.is_active = data['is_active']
        intent.save()
        return Response({'message': 'Updated', 'id': intent.id})
    intent.delete()
    return Response(status=204)