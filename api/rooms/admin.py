from django.contrib import admin
from .models import Room, RoomUser, Question
# Register your models here.
admin.site.register(Room)
admin.site.register(RoomUser)
admin.site.register(Question)