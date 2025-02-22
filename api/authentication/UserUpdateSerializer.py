from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserUpdateSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},  
        }

    def validate(self, data):
        if 'password' in data and data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})

        return data

    def update(self, instance, validated_data):
        validated_data.pop('confirm_password', None)  
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))

        return super().update(instance, validated_data)
