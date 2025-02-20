from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(['POST'])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=400)

    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=400)
    
    login(request, user)
    return Response({'message': 'Login successful'}, status=200)


@api_view(['POST'])
def register_api(request):
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'User already exists'}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already in use'}, status=400)

    user = User.objects.create_user(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        password=password  
    )

    return Response({'message': 'User created successfully'}, status=201)
