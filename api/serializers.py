from rest_framework import serializers
from accounts.models import User, Organization, APIKey
from chat.models import Conversation, Message, AIAgent, Intent, Feedback
from dashboard.models import Analytics, SystemSetting, LogEntry, Notification
from voice.models import VoiceRecording, VoiceSession, SpeechSynthesis, VoiceAnalytics

class UserSerializer(serializers.ModelSerializer):
    """User serializer"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone',
                 'avatar', 'organization', 'language', 'is_admin', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class OrganizationSerializer(serializers.ModelSerializer):
    """Organization serializer"""

    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class ConversationSerializer(serializers.ModelSerializer):
    """Conversation serializer"""
    user = UserSerializer(read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'user', 'organization', 'status', 'title', 'ai_agent',
                 'transferred_to', 'transfer_reason', 'started_at', 'last_message_at',
                 'completed_at', 'message_count', 'ai_responses', 'duration')
        read_only_fields = ('id', 'started_at', 'last_message_at', 'completed_at')

    def get_duration(self, obj):
        return str(obj.duration) if obj.duration else None

class MessageSerializer(serializers.ModelSerializer):
    """Message serializer"""

    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender_type', 'sender', 'content',
                 'content_type', 'timestamp', 'is_read', 'confidence_score',
                 'intent_detected')
        read_only_fields = ('id', 'timestamp')

class AIAgentSerializer(serializers.ModelSerializer):
    """AI Agent serializer"""

    class Meta:
        model = AIAgent
        fields = ('id', 'organization', 'name', 'description', 'avatar', 'status',
                 'model_provider', 'model_name', 'system_prompt', 'temperature',
                 'max_tokens', 'supported_languages', 'primary_language',
                 'voice_enabled', 'file_processing', 'max_consecutive_responses',
                 'handoff_triggers', 'total_conversations', 'total_messages',
                 'average_rating', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'total_conversations',
                           'total_messages', 'average_rating')

class IntentSerializer(serializers.ModelSerializer):
    """Intent serializer"""

    class Meta:
        model = Intent
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class FeedbackSerializer(serializers.ModelSerializer):
    """Feedback serializer"""

    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class AnalyticsSerializer(serializers.ModelSerializer):
    """Analytics serializer"""

    class Meta:
        model = Analytics
        fields = '__all__'

class SystemSettingSerializer(serializers.ModelSerializer):
    """System Setting serializer"""

    class Meta:
        model = SystemSetting
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class LogEntrySerializer(serializers.ModelSerializer):
    """Log Entry serializer"""

    class Meta:
        model = LogEntry
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer"""

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class VoiceRecordingSerializer(serializers.ModelSerializer):
    """Voice Recording serializer"""

    class Meta:
        model = VoiceRecording
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class VoiceSessionSerializer(serializers.ModelSerializer):
    """Voice Session serializer"""

    class Meta:
        model = VoiceSession
        fields = '__all__'
        read_only_fields = ('id', 'started_at', 'last_activity', 'ended_at')

class SpeechSynthesisSerializer(serializers.ModelSerializer):
    """Speech Synthesis serializer"""

    class Meta:
        model = SpeechSynthesis
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class VoiceAnalyticsSerializer(serializers.ModelSerializer):
    """Voice Analytics serializer"""

    class Meta:
        model = VoiceAnalytics
        fields = '__all__'
