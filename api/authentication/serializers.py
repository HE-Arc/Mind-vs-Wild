from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    profile_picture_type = serializers.IntegerField(write_only=True, required=False, default=1)

    class Meta:
        model = User 
        fields = ['id', 'username', 'password', 'email', 'avatar_url', 'profile_picture_type']
        extra_kwargs = {'password': {'write_only': True}}

    def get_avatar_url(self, obj):
        profile = getattr(obj, 'auth_profile', None)
        if profile:
            return profile.get_avatar_url()
        return f"https://robohash.org/{obj.username}?set=set1"

    def create(self, validated_data):
        profile_picture_type = validated_data.pop('profile_picture_type', 1)
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        Profile.objects.create(user=user, profile_picture_type=profile_picture_type)
        return user