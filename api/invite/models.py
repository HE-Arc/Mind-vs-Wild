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
    # Unique token for the invitation
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Expiration date for the invitation
    expires_at = models.DateTimeField() 
    # True if the invitation has been used
    used = models.BooleanField(default=False) 

    def is_valid(self):
        """Checks if the invitation is valid."""
        return (not self.used) and (timezone.now() < self.expires_at)

    def __str__(self):
        return f"Invitation to {self.group.name} by {self.invited_by.username}"
