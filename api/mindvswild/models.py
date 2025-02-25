from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture_type = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"
    
class Group(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups')

    def __str__(self):
        return self.name

class GroupUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('group', 'user')  # Un utilisateur ne peut appartenir qu'une fois à un groupe

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_rooms')
    session_code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.session_code}"


class Question(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=255)
    options = models.JSONField()  # Stocke les options sous forme de JSON

    def __str__(self):
        return self.text
