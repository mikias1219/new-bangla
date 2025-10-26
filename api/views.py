from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from accounts.models import User, Organization
from chat.models import Conversation, Message, AIAgent
from dashboard.models import Analytics
from voice.models import VoiceRecording
from services.openai_service import OpenAIService

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
@permission_classes([AllowAny])
@csrf_exempt
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
@csrf_exempt
def send_chat_message(request):
    """Send a chat message and get AI response"""
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
            # Create new conversation and assign AI agent
            ai_agent = AIAgent.objects.filter(
                organization=request.user.organization,
                status='active'
            ).first()

            conversation = Conversation.objects.create(
                user=request.user,
                organization=request.user.organization,
                ai_agent=ai_agent
            )

        # Create user message
        user_message = Message.objects.create(
            conversation=conversation,
            sender_type='user',
            sender=request.user,
            content=content
        )

        # Initialize response data
        response_data = {
            'conversation_id': conversation.id,
            'user_message_id': user_message.id,
            'status': 'sent'
        }

        # Generate AI response if agent is assigned
        if conversation.ai_agent:
            openai_service = OpenAIService(conversation.organization)

            # Get conversation history
            conversation_messages = Message.objects.filter(
                conversation=conversation
            ).order_by('timestamp')

            # Format messages for OpenAI API
            messages = []
            for msg in conversation_messages:
                if msg.sender_type == 'user':
                    role = 'user'
                elif msg.sender_type == 'ai':
                    role = 'assistant'
                else:
                    continue  # Skip system messages for now

                messages.append({
                    'role': role,
                    'content': msg.content
                })

            # Generate AI response
            ai_response = openai_service.generate_chat_response(
                messages=messages,
                ai_agent=conversation.ai_agent
            )

            if ai_response:
                # Create AI message
                ai_message = Message.objects.create(
                    conversation=conversation,
                    sender_type='ai',
                    content=ai_response,
                    confidence_score=0.9  # Default confidence
                )

                response_data['ai_message'] = {
                    'id': ai_message.id,
                    'content': ai_response,
                    'timestamp': ai_message.timestamp
                }

                # Update conversation stats
                conversation.message_count += 1
                conversation.ai_responses += 1

        # Update conversation stats
        conversation.message_count += 1
        conversation.last_message_at = timezone.now()
        conversation.save()

        return Response(response_data)

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
@csrf_exempt
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
            status='processing',
            file_size=audio_file.size
        )

        # Process voice recording with OpenAI Whisper
        openai_service = OpenAIService(conversation.organization)

        # Get the file path
        file_path = recording.audio_file.path

        # Transcribe the audio
        transcription_result = openai_service.transcribe_audio(file_path)

        if transcription_result['success']:
            recording.status = 'completed'
            recording.transcription = transcription_result['transcription']
            recording.confidence_score = transcription_result['confidence']
            recording.detected_language = transcription_result['language']
            recording.language_confidence = 0.95  # Default for Whisper
        else:
            recording.status = 'failed'
            recording.error_message = transcription_result.get('error', 'Transcription failed')

        recording.processing_completed_at = timezone.now()
        recording.save()

        if recording.status == 'completed':
            # Create a message from the transcription
            message = Message.objects.create(
                conversation=conversation,
                sender_type='user',
                sender=request.user,
                content=recording.transcription,
                content_type='voice',
                voice_recording=recording
            )

            # Update conversation stats
            conversation.message_count += 1
            conversation.last_message_at = timezone.now()
            conversation.save()

            return Response({
                'recording_id': recording.id,
                'transcription': recording.transcription,
                'confidence': recording.confidence_score,
                'message_id': message.id
            })
        else:
            return Response({
                'recording_id': recording.id,
                'error': recording.error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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