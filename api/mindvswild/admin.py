from django.contrib import admin
from .models import Group, GroupUser, Room, Question, Profile, RoomUser, GroupInvitation

admin.site.register(Profile)
admin.site.register(Group)
admin.site.register(GroupUser)
admin.site.register(GroupInvitation)
admin.site.register(Room)
admin.site.register(RoomUser)
admin.site.register(Question)

