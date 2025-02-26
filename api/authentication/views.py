from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer


@api_view(['POST'])
def login_api(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response("missing user", status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})
    

@api_view(['POST'])
def register_api(request):
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
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = request.user

    return Response({
        'user': {
            'username': user.username,
            'email': user.email,
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_user(request):
    user = request.user
    if hasattr(user, 'auth_token'):
        user.auth_token.delete()
    user.delete()

    return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)

