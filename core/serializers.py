from rest_framework import serializers
from .models import (
    Client, BanglaConversation, CallLog, BanglaIntent, 
    AdminProfile, SystemSettings, Analytics
)


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class BanglaConversationSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    
    class Meta:
        model = BanglaConversation
        fields = '__all__'
        read_only_fields = ['created_at']


class CallLogSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    
    class Meta:
        model = CallLog
        fields = '__all__'
        read_only_fields = ['timestamp']


class BanglaIntentSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    
    class Meta:
        model = BanglaIntent
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AdminProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = AdminProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AnalyticsSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    
    class Meta:
        model = Analytics
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
