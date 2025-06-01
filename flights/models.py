from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class Airport(models.Model):
    code = models.CharField(max_length=3)
    city = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.city} ({self.code})"

class Flight(models.Model):
    origin =models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    #duration = models.IntegerField()
    departure_time = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    seats_available = models.IntegerField(default=100)

    def __str__(self):
        return f"Flight from {self.origin} to {self.destination}"
        #return f"{self.id}: {self.origin} to {self.destination}"

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    seat_number = models.CharField(max_length=10)
    status = models.CharField(max_length=20, default="Booked")

    def __str__(self):
        return f"Booking by {self.user.username} for flight {self.flight.origin} -> {self.flight.destination}"

class Seat(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="seats")
    seat_number = models.CharField(max_length=5)
    #row = models.IntegerField()
    #column = models.CharField(max_length=1) # A,B,C...
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{seat_number} - {self.flight}"
