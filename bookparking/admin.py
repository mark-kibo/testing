from django.contrib import admin
from . models import Spaces, Bookings, ReserveUser

# Register your models here.
admin.site.register(Spaces)
admin.site.register(Bookings)
admin.site.register(ReserveUser)