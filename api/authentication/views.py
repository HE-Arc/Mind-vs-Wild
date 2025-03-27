from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from rest_framework.permissions import AllowAny

from .serializers import UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    #print("DEBUG: raw username/password =", repr(request.data['username']), repr(request.data['password']))
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response("incorrect password", status=status.HTTP_401_UNAUTHORIZED)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})
    

@api_view(['POST'])
@permission_classes([AllowAny])
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
            'id': user.id,
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

@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_user(request):
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


