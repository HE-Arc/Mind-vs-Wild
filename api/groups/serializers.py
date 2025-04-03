from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Group, GroupUser


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


class GroupMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GroupUser
        fields = ['user', 'is_admin', 'joined_at']


class GroupSerializer(serializers.ModelSerializer):
    members = GroupMemberSerializer(source='memberships', many=True, read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'created_by', 'created_at', 'members']