from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .models import Room, Group, RoomUser
from .serializers import RoomSerializer

class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Limit to rooms of groups where the user is a member."""
        user = self.request.user
        return Room.objects.filter(group__memberships__user=user).distinct()

    def perform_create(self, serializer):
        """Create a room linked to a group"""
        group_id = self.request.data.get('group')
        group = get_object_or_404(Group, id=group_id)

        # Check if the user is a member of the group
        if not group.memberships.filter(user=self.request.user).exists():
            return Response({"detail": "Vous n'êtes pas membre du groupe."}, status=status.HTTP_403_FORBIDDEN)
        
        # Create the room
        room = serializer.save(group=group, created_by=self.request.user)
        
        # Add the creator as a participant
        RoomUser.objects.create(room=room, user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='join/(?P<code>[^/.]+)')
    def join(self, request, code=None):
        """Join a room by code"""
        room = get_object_or_404(Room, code=code)
        
        # Check if the user is a member of the group linked to the room
        if room.group and not room.group.memberships.filter(user=request.user).exists():
            return Response({"detail": "Vous n'êtes pas membre du groupe."}, status=status.HTTP_403_FORBIDDEN)
        
        # Add the user to the room
        RoomUser.objects.get_or_create(room=room, user=request.user)
        return Response({"detail": "Vous avez rejoint la salle."}, status=status.HTTP_200_OK)
