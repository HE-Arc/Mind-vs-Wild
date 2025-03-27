from django.db import models
import uuid
from django.contrib.auth.models import User
from groups.models import Group



class Room(models.Model):
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE, related_name="rooms")
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms_created")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.name}"

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

