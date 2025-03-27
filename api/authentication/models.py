from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='auth_profile')
    profile_picture_type = models.IntegerField(null=True, blank=True, default=1)

    def __str__(self):
        return f"{self.user.username} Profile"

    def get_avatar_url(self):
        set_type = self.profile_picture_type or 1
        return f"https://robohash.org/{self.user.username}?set=set{set_type}"

