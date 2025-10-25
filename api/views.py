from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q

from accounts.models import User, Organization
from chat.models import Conversation, Message, AIAgent
from dashboard.models import Analytics
from voice.models import VoiceRecording

from .serializers import (
    UserSerializer, OrganizationSerializer, ConversationSerializer,
    MessageSerializer, AIAgentSerializer, AnalyticsSerializer
)

class OrganizationViewSet(viewsets.ModelViewSet):
    """Organization API"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(
            Q(users=self.request.user) | Q(is_active=True)
        )

class ConversationViewSet(viewsets.ModelViewSet):
    """Conversation API"""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(
            Q(user=self.request.user) | Q(organization=self.request.user.organization)
        ).select_related('user', 'ai_agent', 'organization')

class MessageViewSet(viewsets.ModelViewSet):
    """Message API"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            conversation__organization=self.request.user.organization
        ).select_related('conversation', 'sender')

class AIAgentViewSet(viewsets.ModelViewSet):
    """AI Agent API"""
    queryset = AIAgent.objects.all()
    serializer_class = AIAgentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AIAgent.objects.filter(
            organization=self.request.user.organization
        )

class AnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """Analytics API"""
    queryset = Analytics.objects.all()
    serializer_class = AnalyticsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Analytics.objects.filter(
            organization=self.request.user.organization
        )

@api_view(['POST'])
def token_view(request):
    """Token authentication"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current user information"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_chat_message(request):
    """Send a chat message"""
    content = request.data.get('content')
    conversation_id = request.data.get('conversation_id')

    if not content:
        return Response(
            {'error': 'Content is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if conversation_id:
            conversation = Conversation.objects.get(
                id=conversation_id,
                user=request.user
            )
        else:
            # Create new conversation
            conversation = Conversation.objects.create(
                user=request.user,
                organization=request.user.organization
            )

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

        return Response({
            'conversation_id': conversation.id,
            'message_id': message.id,
            'status': 'sent'
        })

    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_voice(request):
    """Process voice recording"""
    audio_file = request.FILES.get('audio')
    conversation_id = request.data.get('conversation_id')

    if not audio_file:
        return Response(
            {'error': 'Audio file is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user
        )

        # Create voice recording record
        recording = VoiceRecording.objects.create(
            user=request.user,
            conversation=conversation,
            audio_file=audio_file,
            status='pending',
            file_size=audio_file.size
        )

        # Here you would trigger voice processing (speech-to-text)
        # For now, we'll just mark it as completed with mock data
        recording.status = 'completed'
        recording.transcription = "This is a mock transcription of the voice message."
        recording.confidence_score = 0.95
        recording.detected_language = 'en'
        recording.language_confidence = 0.98
        recording.save()

        # Create a message from the transcription
        message = Message.objects.create(
            conversation=conversation,
            sender_type='user',
            sender=request.user,
            content=recording.transcription,
            content_type='voice',
            voice_recording=recording
        )

        return Response({
            'recording_id': recording.id,
            'transcription': recording.transcription,
            'confidence': recording.confidence_score
        })

    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback(request):
    """Submit feedback for a conversation"""
    conversation_id = request.data.get('conversation_id')
    rating = request.data.get('rating')
    comment = request.data.get('comment', '')

    if not conversation_id or not rating:
        return Response(
            {'error': 'Conversation ID and rating are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user
        )

        # Create feedback (assuming Feedback model exists)
        # This would need to be implemented based on your Feedback model
        return Response({'status': 'Feedback submitted successfully'})

    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )