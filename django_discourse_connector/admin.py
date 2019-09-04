from django.contrib import admin
from .models import DiscourseClient, DiscourseUser, DiscourseGroup

admin.site.register(DiscourseClient)
admin.site.register(DiscourseGroup)
admin.site.register(DiscourseUser)
