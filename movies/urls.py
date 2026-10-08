from django.urls import path
from . import views

app_name = "movies"

urlpatterns = [
    path("", views.movie_list, name="movie_list"),
    path("movies/<int:pk>/", views.movie_detail, name="movie_detail"),
    path("movies/<int:movie_id>/review/", views.add_review, name="add_review"),
    path("booking/<int:showtime_id>/", views.seat_booking, name="seat_booking"),
    path("booking/confirmation/<int:booking_id>/", views.booking_confirmation, name="booking_confirmation"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
]
