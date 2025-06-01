from django.urls import path
from . import views

app_name = "flights" # this is what sets the namespace

urlpatterns = [
    path("", views.index, name="index"),
    path('<int:flight_id>/book/', views.book_flight, name='book_flight'),
    path('my_bookings/', views.my_bookings, name='my_bookings'), #view for user bookimgs
    path('search/', views.search_flights, name="search_flights"),
    path('book/<int:flight_id>/', views.book_seat, name='book_seat'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/pdf-summary/', views.admin_pdf_summary, name='admin_pdf_summary'),
]