from rest_framework import serializers
from .models import Group, GroupUser, GroupInvitation, Room, RoomUser, Question
from django.contrib.auth.models import User  # Utilisation du modèle User de Django

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class GroupMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Affiche les infos utilisateur

    class Meta:
        model = GroupUser
        fields = ['user', 'is_admin', 'joined_at']

class GroupSerializer(serializers.ModelSerializer):
    members = GroupMemberSerializer(source='memberships', many=True, read_only=True)
    created_by = serializers.StringRelatedField()  # Affiche le username du créateur

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'created_by', 'created_at', 'invite_code', 'members']
        read_only_fields = ['created_by', 'created_at', 'invite_code', 'members']

class RoomParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RoomUser
        fields = ['user', 'joined_at']

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'group', 'created_by', 'created_at', 'code', 'participants', 'is_active']
        read_only_fields = ['code', 'created_by', 'created_at', 'participants']
