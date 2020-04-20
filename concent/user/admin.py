from django.contrib import admin
from user.models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
            'username',
            'email',
            'date_joined',
            )
    list_display_links = (
            'username',
            'email',
            )

