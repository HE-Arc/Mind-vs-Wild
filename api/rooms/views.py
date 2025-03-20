from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .models import Room, Group, RoomUser
from django.db import transaction
from .serializers import RoomSerializer

### Room ViewSet
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'code'  # Use the code instead of the id

    def get_queryset(self):
        """Limit to rooms of groups where the user is a member and public rooms."""
        user = self.request.user
        return Room.objects.filter(
            group__memberships__user=user
        ) | Room.objects.filter(group__isnull=True)
        
    def perform_create(self, serializer):
        """Create a room linked to a group or as a public room"""
        group_id = self.request.data.get('group')
        if group_id:
            group = get_object_or_404(Group, id=group_id)
            # Check if the user is a member of the group
            if not group.memberships.filter(user=self.request.user).exists():
                return Response({"detail": "Vous n'êtes pas membre du groupe."}, status=status.HTTP_403_FORBIDDEN)
            # Create the room linked to the group
            room = serializer.save(group=group, created_by=self.request.user)
        else:
            # Create a public room
            room = serializer.save(created_by=self.request.user)
        
        # Add the creator as a participant
        RoomUser.objects.create(room=room, user=self.request.user)
        
        # Return the created room's details
        return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, code=None):
        """Join a room by code"""
        room = get_object_or_404(Room, code=code)
        
        # Check if the user is a member of the group linked to the room
        if room.group and not room.group.memberships.filter(user=request.user).exists():
            return Response({"detail": "Vous n'êtes pas membre du groupe."}, status=status.HTTP_403_FORBIDDEN)
        # Add the user to the room
        RoomUser.objects.get_or_create(room=room, user=request.user)
        return Response({
            "detail": "Vous avez rejoint la salle.",
            "room": RoomSerializer(room).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def leave(self, request, code=None):
        """Leave a room"""
        room = get_object_or_404(Room, code=code)
        user = request.user

        # Check if the user is a member of the room
        participation = RoomUser.objects.filter(room=room, user=user).first()
        if not participation:
            return Response({"detail": "Vous n'êtes pas membre de la salle."}, status=status.HTTP_403_FORBIDDEN)

        # If the user is the creator, delete the room
        if room.created_by == user:
            with transaction.atomic():
                room.delete()
                return Response({"detail": "Salle supprimée."}, status=status.HTTP_200_OK)

        # If the user is not the creator, they can leave the room
        participation.delete()
        return Response({"detail": "Vous avez quitté la salle."}, status=status.HTTP_200_OK)
    