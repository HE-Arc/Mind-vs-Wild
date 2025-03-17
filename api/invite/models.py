from django.utils import timezone  
from django.db import models
from django.contrib.auth.models import User
from groups.models import Group


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
