from django.contrib import admin
from .models import Airport, Flight, Seat, Booking

# Register your models here.
admin.site.register(Airport)
admin.site.register(Flight)

#class SeatInline(admin.TabularInline):
    #model = Seat
    #extra = 0

#@admin.register(Flight)
#class FlightAdmin(admin.ModelAdmin):
    #list_display = ('id', 'origin', 'destination', 'departure_time', 'arrival_time')
    #inlines = [SeatInline]

#@admin.register(Booking)
#class BookingAdmin(admin.ModelAdmin):
    #list_display = ('user', 'flight', 'seat', 'booking_time')

#@admin.register(Seat)
#class SeatAdmin(admin.ModelAdmin):
    #list_display = ('seat_number', 'flight', 'is_booked')
