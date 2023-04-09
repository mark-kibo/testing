from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from simple_history.models import HistoricalRecords
from django.utils import timezone
import geocoder
import uuid
# Create your models here.



# create client/staff table
class ReserveUser(AbstractUser):
    is_customer = models.BooleanField('is_customer', default=False)
    is_employee = models.BooleanField('is_employee', default=False)

# table for available spaces at a certain location
class Location(models.Model):
    name = models.CharField(max_length=255)
    capacity = models.IntegerField(default=0)
    pricing_per_hour= models.IntegerField(default=0)
    name_image=models.ImageField(upload_to="media/")
    current_capacity = models.IntegerField(default=0)  # Current number of spaces in use


    def __str__(self):
        return self.name

    
class ParkingSpace(models.Model):
    name = models.CharField(max_length=200)
    capacity = models.IntegerField(default=1)
    is_booked = models.BooleanField(default=False)
    location = models.ForeignKey(to=Location, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def is_available(self, check_in, check_out):
        """Check if the space is available for the specified time range"""
        if self.is_booked:
            # Space is already booked
            return False
        for booking in self.booking_set.all():
            if not (check_out <= booking.check_in or check_in >= booking.checkout):
                # Space is not available for the specified time range
                return False
        return True


class Booking(models.Model):
    space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    client = models.ForeignKey(ReserveUser, on_delete=models.CASCADE)
    check_in = models.DateTimeField()
    checkout = models.DateTimeField(null=True)
    has_expired = models.BooleanField(default=False)
    government_id= models.CharField(max_length=8, primary_key=False, unique=False, null=True)
    car_plate = models.CharField(max_length=255, null=True, unique=False)
    

    def __str__(self):
        return f'{self.space} booking ({self.check_in} - {self.checkout})'


    def is_expired(self):
        """Check if the booking time has expired"""
        now = datetime.now()
        if self.checkout:
            return self.checkout.strftime('%Y-%m-%d %H:%M:%S') < now.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return False






acces_token='pk.eyJ1Ijoid2F3ZXJ1ZnJhIiwiYSI6ImNsZjd2OWE3YjAyOWYzeXBubTgxdzJyeDgifQ.JNJMOHwkX74B3jLDv1PYeg'

    

choices=(('paid','paid'),('not paid', 'not paid'))
class Payout(models.Model):
    transaction_id=models.UUIDField(unique=True, auto_created=True)
    space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    client = models.ForeignKey(ReserveUser, on_delete=models.CASCADE, null=True)
    payment_amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=choices)
    payment_method = models.CharField(max_length=50)

    def __str__(self):
        return self.space.name
