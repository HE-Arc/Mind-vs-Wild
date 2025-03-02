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

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    # Retourne les groupes où l'utilisateur est membre
    def get_queryset(self):
        """Limite l'affichage aux groupes dont l'utilisateur est membre"""
        user = self.request.user
        return Group.objects.filter(memberships__user=user).distinct()

    # Enregistre le créateur du groupe comme admin
    def perform_create(self, serializer):
        """Ajoute le créateur du groupe comme admin"""
        group = serializer.save(created_by=self.request.user)
        GroupUser.objects.create(group=group, user=self.request.user, is_admin=True)
        return group

    # Invite un utilisateur dans le groupe
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def invite(self, request, pk=None):
        """Créer une invitation pour rejoindre le groupe (avec token)"""
        group = self.get_object()
        # Vérif admin
        membership = GroupUser.objects.filter(group=group, user=request.user, is_admin=True).first()
        if not membership:
            return Response({"detail": "Permission refusée. Seul un admin peut inviter."},
                            status=status.HTTP_403_FORBIDDEN)

        username = request.data.get('username', None)
        # Si un username est fourni, c'est une invitation nominative.
        invited_user = None
        if username:
            try:
                invited_user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"detail": "Utilisateur introuvable."}, 
                                status=status.HTTP_400_BAD_REQUEST)
            # Vérifier s'il est déjà dans le groupe
            if GroupUser.objects.filter(group=group, user=invited_user).exists():
                return Response({"detail": "Cet utilisateur est déjà membre du groupe."}, 
                                status=status.HTTP_400_BAD_REQUEST)
        
        # Générer un token
        token = secrets.token_urlsafe(16)
        # Expiration dans 7 jours, par exemple
        expires_at = timezone.now() + timedelta(days=7)

        invitation = GroupInvitation.objects.create(
            group=group,
            invited_by=request.user,
            invited_user=invited_user,  # peut être None si on veut un lien "générique"
            token=token,
            expires_at=expires_at
        )

        # Construire l'URL d'invitation (côté frontend, par exemple)
        # On suppose que le front a une route /accept-invite/:token
        invite_url = f"{request.scheme}://{request.get_host()}/#/accept-invite/{token}"

        return Response({
            "invite_token": token,
            "invite_url": invite_url,
            "expires_at": expires_at,
            "invited_user": username if username else None
        }, status=status.HTTP_201_CREATED)
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def leave(self,request,pk=None):
        """Quitter un groupe"""
        group = self.get_object()
        user = request.user
        
        # Vérifier que l'utilisateur est membre du groupe
        membership = GroupUser.objects.filter(group=group, user=user).first()
        if not membership:
            return Response({"detail": "Vous n'êtes pas membre de ce groupe."}, status=status.HTTP_403_FORBIDDEN)
        
        # Si l'utilisateur est admin, vérifier s'il est le dernier membre
        if membership.is_admin:
            members_count = GroupUser.objects.filter(group=group).count()
            
            if members_count > 1:
                # Si d'autres membres existent, il doit transférer son rôle d'admin
                return Response({
                    "detail": "Vous êtes l'admin de ce groupe. Transférez le rôle d'admin à un autre membre avant de quitter."
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Si c'est le dernier membre, on supprime le groupe
                with transaction.atomic():
                    group.delete()
                    return Response({"detail": "Groupe supprimé car vous étiez le dernier membre."}, status=status.HTTP_200_OK)
        
        # Si l'utilisateur n'est pas admin, il peut quitter le groupe
        membership.delete()
        return Response({"detail": "Vous avez quitté le groupe."}, status=status.HTTP_200_OK)

### Room ViewSet
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'code'  # Utiliser le code au lieu de l'id

    def get_queryset(self):
        """Limiter aux rooms des groupes dont l'utilisateur est membre."""
        user = self.request.user
        return Room.objects.filter(group__memberships__user=user).distinct()

    def perform_create(self, serializer):
        """Créer une room liée à un groupe"""
        group_id = self.request.data.get('group')
        group = get_object_or_404(Group, id=group_id)

        # Vérifier que l'utilisateur est membre du groupe
        if not group.memberships.filter(user=self.request.user).exists():
            return Response({"detail": "Vous n'êtes pas membre de ce groupe."}, status=status.HTTP_403_FORBIDDEN)
        
        # Créer la room
        room = serializer.save(group=group, created_by=self.request.user)
        
        # Ajouter le créateur comme participant
        RoomUser.objects.create(room=room, user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, code=None):
        """Rejoindre une room par code"""
        room = get_object_or_404(Room, code=code)
        
        # Vérifier que l'utilisateur est membre du groupe lié à la room
        if room.group and not room.group.memberships.filter(user=request.user).exists():
            return Response({"detail": "Vous n'êtes pas membre du groupe lié à cette room."}, status=status.HTTP_403_FORBIDDEN)
        
        # Ajouter l'utilisateur à la room
        RoomUser.objects.get_or_create(room=room, user=request.user)
        return Response({"detail": "Vous avez rejoint la room."}, status=status.HTTP_200_OK)
    
class AcceptInviteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, token):
        """Accepter une invitation via token"""
        try:
            invitation = GroupInvitation.objects.get(token=token)
        except GroupInvitation.DoesNotExist:
            return Response({"detail": "Invitation invalide ou inexistante."}, 
                            status=status.HTTP_404_NOT_FOUND)

        # Vérifier validité (expiration, used)
        if not invitation.is_valid():
            return Response({"detail": "Invitation expirée ou déjà utilisée."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Si invitation nominative, s'assurer que c'est la bonne personne
        if invitation.invited_user:
            if invitation.invited_user != request.user:
                return Response({"detail": "Cette invitation n'est pas pour cet utilisateur."}, 
                                status=status.HTTP_403_FORBIDDEN)
        else:
            # invitation "générique" => pas de check sur invited_user
            pass

        # Vérifier si déjà membre
        group = invitation.group
        if GroupUser.objects.filter(group=group, user=request.user).exists():
            return Response({"detail": "Vous êtes déjà membre de ce groupe."},
                            status=status.HTTP_400_BAD_REQUEST)

        # OK, on ajoute l'utilisateur au groupe
        GroupUser.objects.create(group=group, user=request.user, is_admin=False)

        # Marquer l'invitation comme utilisée pour qu'on ne puisse plus la réutiliser
        invitation.used = True
        invitation.save()

        # Renvoyer les infos du groupe
        serializer = GroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)