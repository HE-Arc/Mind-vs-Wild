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
    # True if the user is an admin of the group
    is_admin = models.BooleanField(default=False)  
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can only be in a group once
        unique_together = ('group', 'user')  

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


    