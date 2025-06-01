from django import forms
from .models import Booking, Flight

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['flight', 'seat_number']

    seat_number = forms.CharField(max_length=10, label="seat Number")
    flight = forms.ModelChoiceField(queryset=Flight.objects.all(), label="Select Fligt")
