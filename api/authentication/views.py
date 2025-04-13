from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer

class AuthenticationViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        if not user.check_password(request.data['password']):
            return Response("incorrect password", status=status.HTTP_401_UNAUTHORIZED)
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return Response({'token': token.key, 'user': serializer.data})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(username=serializer.validated_data['username']).exists():
                return Response({'message': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
            user = serializer.save()
            user.set_password(serializer.validated_data['password'])
            user.save()
            token = Token.objects.create(user=user)
            return Response({
                'message': 'User registered successfully',
                'user': serializer.data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], authentication_classes=[TokenAuthentication], permission_classes=[IsAuthenticated])
    def get_user(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], authentication_classes=[TokenAuthentication], permission_classes=[IsAuthenticated])
    def logout(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], authentication_classes=[TokenAuthentication], permission_classes=[IsAuthenticated])
    def delete_user(self, request):
        user = request.user
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], authentication_classes=[TokenAuthentication], permission_classes=[IsAuthenticated])
    def update_user(self, request):
        user = request.user
        data = request.data.copy()
        blocked_fields = ['is_staff', 'is_superuser']
        for field in blocked_fields:
            data.pop(field, None)
        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            if 'password' in data:
                user.set_password(data['password'])
                user.save()
            else:
                serializer.save()
            return Response({'message': 'User updated successfully', 'user': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'], authentication_classes=[TokenAuthentication], permission_classes=[IsAuthenticated])
    def update_avatar_type(self, request):
        if 'profile_picture_type' not in request.data:
            return Response({'error': 'profile_picture_type is required'}, status=status.HTTP_400_BAD_REQUEST)
        picture_type = int(request.data['profile_picture_type'])
        if not (1 <= picture_type <= 4):
            return Response({'error': 'profile_picture_type must be between 1 and 4'}, status=status.HTTP_400_BAD_REQUEST)
        profile = request.user.profile
        profile.profile_picture_type = picture_type
        profile.save()
        serializer = UserSerializer(request.user)
        return Response({'message': 'Avatar type updated successfully', 'user': serializer.data}, status=status.HTTP_200_OK)


