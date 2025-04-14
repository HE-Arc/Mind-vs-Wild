from rest_framework import serializers
from .models import User, RoomUser, Room


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar_url']
        
    def get_avatar_url(self, obj):
        profile = getattr(obj, 'auth_profile', None)
        if profile:
            return profile.get_avatar_url()
        return f"https://robohash.org/{obj.username}?set=set1"

class RoomParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = RoomUser
        fields = ['user', 'joined_at']

class RoomSerializer(serializers.ModelSerializer):
    participants = RoomParticipantSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True) 
    
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'group', 'created_by', 'created_at', 'participants', 'is_active'
        ]
        read_only_fields = ['created_by', 'created_at', 'participants']