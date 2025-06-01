from django.shortcuts import render, get_object_or_404, redirect
from .models import Flight, Booking
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.admin.views.decorators import staff_member_required
import stripe
import json
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from datetime import datetime
from reportlab.pdfgen import canvas
# Create your views here.
@login_required
def index(request):
    flights = Flight.objects.all()
    return render(request, "flights/index.html", {
        "flights": flights
    })

def flight(request, flight_id):
    flight = Flight.objects.get(id=flight_id)
    return render(request, "flights/flight.html", {
        "flight":flight
    })

@login_required
def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.flight = flight
            booking.save()
            return redirect("flights:index")

    else:
        form = BookingForm()

    return render(request, 'flights/book_flight.html', {'flight': flight, 'form': form})

def search_flights(request):
    flights = []
    if request.method == 'GET':
        origin = request.GET.get("origin")
        destination = request.GET.get("destination")
        if origin and destination:
            flights = Flight.objects.filter(origin_icontains=origin, destination_icontains=destination)
    return render(request, "flights/search.html", {'flights':flights})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'flights/my_bookings.html', {'bookings': bookings})

def book_seat(request, flight_id):
    flight = Flight.objects.get(pk=flight_id)
    if flight.seats_available > 0:
        flight.seats_available -= 1
        flight.save()
        return render(request, 'flights/confirmation.html', {'flight':flight})
    return render(request, 'flights/unavailable.html', {'flight':flight})

def flight_detail(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    seats = Seat.objects.filter(flight=flight)
    return render(request, "flights/flights_detail.html", {'flight': flight, 'seats': seats})

def seat_map_view(request, flight_id):
    flight = Flight.objects.get(id=flight_id)
    seat = Seat.objects.filter(flight=flight).order_by('row', 'column')

    seat_rows =[]
    current_row = []
    current_row_number = None
    for seat in seats:
        if seat.row != current_row_number:
            if current_row:
                seat_rows.append(current_row)
            current_row =[seat]
            current_row_number = seat.row
        else:
            current_row.append(seat)
    if current_row:
        seat_rows.append(current_row)

    if request.method == "POST":
        seat_id = request.POST.get('seat_id')
        seat = Seat.objects.get(id=seat_id)
        seat.is_booked = True
        seat.save()
        # Redirect to payment
        return redirect('inituate_payment', seat_id=seat_id)

    return render(request, 'flights/seat_map.html', {
        'flight': flight,
        'seat_rows': seat_rows
    })

def confirm_booking(request,booking_id):
    booking = Booking.objects.get(id=booking_id)
    #( send user email, etc)
    admin_emails = [admin.email for admin in User.objects.filter(is_staff=True)]
    send_mail(
        'New Booking Notification',
        f"{booking.user} booked {booking.flight}",
        'admin@yourairline.com',
        admin_emails
    )

def register_user(request):
    # after user is saved
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verify_url = request.build_absolute_uri(reverse('verify_email', args=[uid, token]))

    send_mail(
        'Verify your account',
        f"Click to verify: {verify_url}",
        'no-reply@yourairline.com',
        [user.email]
    )

def verify_email(request, uid64, token):
    uid = urlsafe_base64_decode(uid64).decode()
    user = User.objects.get(pk=uid)
    if default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        return redirect('login')


@staff_member_required
def admin_dashboard(request):
    flights = Flight.objects.all()
    # aggregate bookings per flight
    flight_labels = []
    flight_counts = []
    for flight in flights:
        flight_labels.append(f"{flight.origin} -> {flight.destination}")
        count = Booking.objects.filter(flight=flight).count()
        flight_counts.append(count)

    # Total Bookings
    total_bookings = Booking.objects.count()
    
    #top 3 most booked flights
    top_flights = (Booking.objects.values('flight__origin', 'flight__destination').annotate(count=Count('id')).order_by('-count')[:3])

    # bookings per month
    monthly_bookings =(Booking.objects.annotate(month=TruncMonth('booking_date')).values('month').annotate(count=Count('id')).order_by('month'))

    month_labels = [b['month'].strftime("%b %Y") for b in monthly_bookings]
    month_counts = [b['count'] for b in monthly_bookings]
        
    context = {
        'flight_labels_json': json.dumps(flight_labels),
        'flight_counts_json': json.dumps(flight_counts),
        'month_labels_json': json.dumps(month_labels),
        'month_counts_json': json.dumps(month_counts),
        'total_bookings': total_bookings,
        'top_flights': top_flights,
        #'booking_data': booking_data,
    }
    return render(request, 'flights/admin_dashboard.html', context)

    # prepare data for chart




#stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request,booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data':{'name': f"Flight {booking.flight}"},
                'unit_ammount': int(booking.price * 100),
            },
            'quantity':1,
        }],
        mode='payment',
        success_url='http://localhost:8000/success/',
        cancel_url='http://localhost:8000/cancel/',
    )
    return redirect(session.url, code=303)


def admin_pdf_summary(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="booking_summary.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 14)
    p.drawString(100, 800, "Booking Summary Report")

    y = 760
    bookings = Booking.objects.select_related("flight").all()

    for booking in bookings:
        p.drawString(80, y, f"Flight: {booking.flight.origin} -> {booking.flight.destination} | Passenger:")
        y -= 20
        if y < 100:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response

    