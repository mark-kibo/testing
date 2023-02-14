from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from simple_history.models import HistoricalRecords

# Create your models here.



# create client/staff table
class ReserveUser(AbstractUser):
    is_customer = models.BooleanField('is_customer', default=False)
    is_employee = models.BooleanField( 'is_employee', default=False)


# table for available spaces at a certain location
class Spaces(models.Model):
    parking_location = models.CharField(max_length=255)
    number_of_spaces = models.IntegerField(default=0)
    pricing_per_hour= models.IntegerField(default=0)
    location_image=models.ImageField(upload_to="media/")

    def __str__(self):
        return self.parking_location

    

# table for user bookings(booked parking spaces)
class Bookings(models.Model):
    client=models.OneToOneField(to=ReserveUser , on_delete=models.SET_NULL, null=True , unique=False)
    location = models.ForeignKey(to=Spaces, null=True, on_delete=models.SET_NULL)
    government_id= models.CharField(max_length=8, primary_key=True)
    car_plate = models.CharField(max_length=255)
    check_in_date=models.DateField(default=datetime.now().strftime("%Y/%m/%d"))
    check_out_date=models.DateField(default=datetime.now().strftime("%Y/%m/%d"))
    check_in_time=models.TimeField()
    check_out_time=models.TimeField()

    history=HistoricalRecords()

    is_paid=models.BooleanField(default=False)





