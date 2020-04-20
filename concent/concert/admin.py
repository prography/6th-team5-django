from django.contrib import admin

from concert.models import *


admin.site.register(Artist)
admin.site.register(Concert)
admin.site.register(Price)

