from datetime import date, time
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from movies.models import Movie, Showtime, SeatBooking, MovieReview
from movies.forms import SeatBookingForm, MovieReviewForm


class MoviePortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.movie = Movie.objects.create(
            title="Dune Test Saga",
            genre="Sci-Fi",
            duration=165,
            release_date=date(2024, 3, 1),
            poster_url="https://example.com/poster.jpg",
            description="A journey across the desert planet.",
        )
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            show_date=date(2026, 10, 10),
            show_time=time(19, 30),
            ticket_price=Decimal("15.00"),
            screen_number="Screen 1 (IMAX)",
        )
        # Pre-book seats A1 and A2
        self.existing_booking = SeatBooking.objects.create(
            showtime=self.showtime,
            customer_name="Existing Customer",
            customer_email="existing@example.com",
            customer_phone="1234567890",
            selected_seats="A1, A2",
            total_paid=Decimal("30.00"),
        )

    def test_movie_list_view(self):
        response = self.client.get(reverse("movies:movie_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dune Test Saga")
        self.assertContains(response, "Sci-Fi")

    def test_movie_detail_view(self):
        response = self.client.get(reverse("movies:movie_detail", args=[self.movie.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dune Test Saga")
        self.assertContains(response, "Screen 1 (IMAX)")

    def test_seat_booking_page_renders_booked_seats(self):
        response = self.client.get(reverse("movies:seat_booking", args=[self.showtime.id]))
        self.assertEqual(response.status_code, 200)
        # A1 and A2 should be marked booked
        self.assertContains(response, 'data-seat-code="A1"')
        self.assertContains(response, 'data-seat-code="A2"')

    def test_duplicate_seat_booking_rejected(self):
        """Verify business logic: prevent a seat from being booked twice for same showtime."""
        form_data = {
            "customer_name": "Bob Duplicate",
            "customer_email": "bob@example.com",
            "customer_phone": "9998887777",
            "selected_seats": "A1, B1",  # A1 is already booked!
        }
        form = SeatBookingForm(data=form_data, showtime=self.showtime)
        self.assertFalse(form.is_valid())
        self.assertIn("already booked", str(form.errors))

    def test_successful_seat_booking_workflow(self):
        """Verify successful booking creates record and server recalculates total paid."""
        form_data = {
            "customer_name": "Alice Fresh",
            "customer_email": "alice@example.com",
            "customer_phone": "5551234567",
            "selected_seats": "B1, B2",  # 2 seats * 15.00 = 30.00
        }
        response = self.client.post(reverse("movies:seat_booking", args=[self.showtime.id]), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirects to confirmation
        
        booking = SeatBooking.objects.filter(customer_email="alice@example.com").first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.total_paid, Decimal("30.00"))
        self.assertTrue(booking.booking_code.startswith("TKT-"))
        self.assertEqual(booking.seats_list(), ["B1", "B2"])

    def test_invalid_seat_code_rejected(self):
        """Seats outside 5x8 grid (e.g. Z9) must be rejected."""
        form_data = {
            "customer_name": "Hacker",
            "customer_email": "hacker@example.com",
            "customer_phone": "1234567890",
            "selected_seats": "Z9",
        }
        form = SeatBookingForm(data=form_data, showtime=self.showtime)
        self.assertFalse(form.is_valid())
        self.assertIn("Invalid seat code", str(form.errors))

    def test_review_submission_and_average_rating(self):
        """Verify 1-5 star review submission and average calculation."""
        response = self.client.post(reverse("movies:add_review", args=[self.movie.id]), data={
            "reviewer_name": "Film Critic",
            "rating": 5,
            "comment": "Spectacular cinematography and sound design!",
        })
        self.assertEqual(response.status_code, 302)
        
        review = MovieReview.objects.filter(movie=self.movie, reviewer_name="Film Critic").first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)
        self.assertEqual(self.movie.average_rating(), 5.0)

    def test_review_rating_bounds(self):
        """Rating must be between 1 and 5."""
        form_bad_high = MovieReviewForm(data={"reviewer_name": "Test", "rating": 6, "comment": "Too high"})
        self.assertFalse(form_bad_high.is_valid())

        form_bad_low = MovieReviewForm(data={"reviewer_name": "Test", "rating": 0, "comment": "Too low"})
        self.assertFalse(form_bad_low.is_valid())

    def test_my_bookings_lookup(self):
        response = self.client.get(reverse("movies:my_bookings") + "?q=existing@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.existing_booking.booking_code)
        self.assertContains(response, "Existing Customer")
