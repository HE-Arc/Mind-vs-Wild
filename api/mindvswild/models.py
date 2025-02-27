from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture_type = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="groups_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    invite_code = models.CharField(max_length=10, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Génère un code d'invitation unique lors de la création du groupe"""
        if not self.invite_code:
            import uuid
            self.invite_code = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

class GroupUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_memberships")
    is_admin = models.BooleanField(default=False)  # True pour le créateur/admin du groupe
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')  # Un utilisateur ne peut appartenir qu'une fois à un groupe

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

class GroupInvitation(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="invitations")
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invitations_sent")
    invited_user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE, related_name="invitations_received"
    )
    token = models.CharField(max_length=64, unique=True)  # Token unique d'invitation
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # Date d'expiration de l'invitation
    used = models.BooleanField(default=False)  # Pour marquer les invitations déjà utilisées

    def is_valid(self):
        """Vérifie si l'invitation est valide (pas expirée ni déjà utilisée)."""
        return (not self.used) and (timezone.now() < self.expires_at)

    def __str__(self):
        return f"Invitation to {self.group.name} by {self.invited_by.username}"

class Room(models.Model):
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE, related_name="rooms")
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms_created")
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # Code unique pour lien d'accès
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.name} ({self.code})"

class RoomUser(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="room_participations")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('room', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.room.name}"

class Question(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=255)
    options = models.JSONField()  # Stocke les options sous forme de JSON

    def __str__(self):
        return self.text
