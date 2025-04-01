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
    participants = RoomParticipantSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)  # Utiliser UserSerializer pour created_by également
    
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'group', 'created_by', 'created_at', 'participants', 'is_active'
        ]
        read_only_fields = ['created_by', 'created_at', 'participants']