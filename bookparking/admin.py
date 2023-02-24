from django.contrib import admin
from . models import ParkingSpace, Booking, ReserveUser, Location

# Register your models here.
admin.site.register(ParkingSpace)
admin.site.register(Location)
admin.site.register(Booking)
admin.site.register(ReserveUser)