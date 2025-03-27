from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
import secrets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Group, GroupUser, GroupInvitation, Room, RoomUser
from .serializers import GroupSerializer, RoomSerializer
from django.contrib.auth.models import User
from django.db import transaction
import environ

env = environ.Env()

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    # Return the groups where the user is a member
    def get_queryset(self):
        """Limit the display to groups where the user is a member"""
        user = self.request.user
        return Group.objects.filter(memberships__user=user).distinct()

    # Save the group creator as admin
    def perform_create(self, serializer):
        """Add the group creator as admin"""
        group = serializer.save(created_by=self.request.user)
        GroupUser.objects.create(group=group, user=self.request.user, is_admin=True)
        return group

    # Invite a user to the group
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def invite(self, request, pk=None):
        """Create an invitation to join the group (with token)"""
        group = self.get_object()
        membership = GroupUser.objects.filter(group=group, user=request.user, is_admin=True).first()
        if not membership:
            return Response({"detail": "Refusé, vous n'êtes pas administrateur du groupe."},
                            status=status.HTTP_403_FORBIDDEN)

        username = request.data.get('username', None)
        # If a username is provided, it's a nominative invitation.
        invited_user = None
        if username:
            try:
                invited_user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"detail": "Utilisateur non trouvé."}, 
                                status=status.HTTP_400_BAD_REQUEST)
            # Check if the user is already in the group
            if GroupUser.objects.filter(group=group, user=invited_user).exists():
                return Response({"detail": "Utilisateur déjà membre du groupe."}, 
                                status=status.HTTP_400_BAD_REQUEST)
        
        # Generate a token
        token = secrets.token_urlsafe(16)
        # Expiration in 7 days
        expires_at = timezone.now() + timedelta(days=7)

        invitation = GroupInvitation.objects.create(
            group=group,
            invited_by=request.user,
            invited_user=invited_user,  
            token=token,
            expires_at=expires_at
        )

        # Build the invitation URL (frontend side, for example)
        FRONT_URL = env('FRONTEND_URL', default='http://localhost:8000')
        invite_url = f"{FRONT_URL}/groups/accept-invite/{token}"

        return Response({
            "invite_token": token,
            "invite_url": invite_url,
            "expires_at": expires_at,
            "invited_user": username if username else None
        }, status=status.HTTP_201_CREATED)
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def leave(self,request,pk=None):
        """Leave a group"""
        group = self.get_object()
        user = request.user
        
        # Check if the user is a member of the group
        membership = GroupUser.objects.filter(group=group, user=user).first()
        if not membership:
            return Response({"detail": "Vous n'êtes pas membre du groupe."}, status=status.HTTP_403_FORBIDDEN)
        
        # If the user is an admin, check if they are the last member
        if membership.is_admin:
            members_count = GroupUser.objects.filter(group=group).count()
            
            if members_count > 1:
                # If other members exist, they must transfer their admin role
                return Response({
                    "detail": "Vous êtes le dernier administrateur du groupe. Vous devez transférer votre rôle avant de quitter le groupe."
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # If they are the last member, delete the group
                with transaction.atomic():
                    group.delete()
                    return Response({"detail": "Groupe supprimé."}, status=status.HTTP_200_OK)
        
        # If the user is not an admin, they can leave the group
        membership.delete()
        return Response({"detail": "Vous avez quitté le groupe."}, status=status.HTTP_200_OK)

class AcceptInviteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, token):
        """Accept an invitation via token"""
        try:
            invitation = GroupInvitation.objects.get(token=token)
        except GroupInvitation.DoesNotExist:
            return Response({"detail": "Invitation invalide."}, 
                            status=status.HTTP_404_NOT_FOUND)

        # Check validity (expiration, used)
        if not invitation.is_valid():
            return Response({"detail": "Invitation expirée ou déjà utilisée."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # If nominative invitation, ensure it's the right person
        if invitation.invited_user:
            if invitation.invited_user != request.user:
                return Response({"detail": "Cette invitation n'est pas destinée à vous."},
                                status=status.HTTP_403_FORBIDDEN)
        else:
            # "Generic" invitation => no check on invited_user
            pass

        # Check if already a member
        group = invitation.group
        if GroupUser.objects.filter(group=group, user=request.user).exists():
            return Response({"detail": "Vous êtes déjà membre du groupe."},
                            status=status.HTTP_400_BAD_REQUEST)

        # OK, add the user to the group
        GroupUser.objects.create(group=group, user=request.user, is_admin=False)

        # Mark the invitation as used so it can't be reused
        invitation.used = True
        invitation.save()

        # Return the group info
        serializer = GroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)