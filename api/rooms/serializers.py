from rest_framework import serializers
from .models import User, RoomUser, Room



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RoomParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = RoomUser
        fields = ['user', 'joined_at']

class RoomSerializer(serializers.ModelSerializer):
    participants = RoomParticipantSerializer(source='participants', many=True, read_only=True)
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'group', 'created_by', 'created_at',
            'code', 'participants', 'is_active'
        ]
        read_only_fields = ['code', 'created_by', 'created_at', 'participants']