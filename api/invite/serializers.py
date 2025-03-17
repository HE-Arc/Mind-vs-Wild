from rest_framework import serializers
from .models import User, Group
from groups.models import GroupUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class GroupMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GroupUser
        fields = ['user', 'is_admin', 'joined_at']

class GroupSerializer(serializers.ModelSerializer):
    members = GroupMemberSerializer(source='memberships', many=True, read_only=True)
    created_by = serializers.StringRelatedField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'created_by', 'created_at', 'members']