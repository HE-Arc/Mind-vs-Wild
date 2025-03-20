from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import GroupInvitation
from groups.models import GroupUser
from .serializers import GroupSerializer

class InviteViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='(?P<token>[^/.]+)')
    def accept_invite(self, request, token=None):
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
        if invitation.invited_user and invitation.invited_user != request.user:
            return Response({"detail": "Cette invitation n'est pas destinée à vous."},
                            status=status.HTTP_403_FORBIDDEN)
        
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
