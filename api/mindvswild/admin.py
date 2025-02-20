from django.contrib import admin
from .models import Group, GroupUser, Room, Question, Profile

admin.site.register(Profile)
admin.site.register(Group)
admin.site.register(GroupUser)
admin.site.register(Room)
admin.site.register(Question)

