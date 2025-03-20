from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="groups_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GroupUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_memberships")
    is_admin = models.BooleanField(default=False)  # True pour le créateur/admin du groupe
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')  # Un utilisateur ne peut appartenir qu'une fois à un groupe

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


    