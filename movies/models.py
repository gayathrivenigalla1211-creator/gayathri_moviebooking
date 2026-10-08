from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Movie(models.Model):
    GENRE_CHOICES = [
        ("Action", "Action"),
        ("Sci-Fi", "Sci-Fi"),
        ("Drama", "Drama"),
        ("Animation", "Animation"),
        ("Comedy", "Comedy"),
        ("Thriller", "Thriller"),
        ("Horror", "Horror"),
        ("Adventure", "Adventure"),
        ("Romance", "Romance"),
    ]

    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    release_date = models.DateField()
    poster_url = models.URLField(max_length=500)
    description = models.TextField()

    class Meta:
        ordering = ["-release_date", "title"]

    def __str__(self):
        return self.title

    @property
    def formatted_duration(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        return f"{minutes}m"

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            avg = sum(r.rating for r in reviews) / reviews.count()
            return round(avg, 1)
        return None

    def review_count(self):
        return self.reviews.count()

    def upcoming_showtimes(self):
        now = timezone.now()
        today = now.date()
        current_time = now.time()
        # Return showtimes today or in the future
        return self.showtimes.filter(
            models.Q(show_date__gt=today) |
            models.Q(show_date=today, show_time__gte=current_time)
        ).order_by("show_date", "show_time")


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="showtimes")
    show_date = models.DateField()
    show_time = models.TimeField()
    ticket_price = models.DecimalField(max_digits=6, decimal_places=2)
    screen_number = models.CharField(max_length=50, default="Screen 1")

    class Meta:
        ordering = ["show_date", "show_time"]

    def __str__(self):
        return f"{self.movie.title} - {self.show_date} {self.show_time.strftime('%H:%M')} ({self.screen_number})"

    def get_booked_seats_list(self):
        """Returns a sorted list of all seat identifiers already booked for this showtime."""
        seats = set()
        for booking in self.bookings.all():
            if booking.selected_seats:
                for seat in booking.selected_seats.split(","):
                    seat_clean = seat.strip().upper()
                    if seat_clean:
                        seats.add(seat_clean)
        return sorted(list(seats))

    @property
    def total_seats(self):
        return 40  # 5 rows (A-E) x 8 columns (1-8)

    @property
    def available_seats_count(self):
        return max(0, self.total_seats - len(self.get_booked_seats_list()))


class SeatBooking(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name="bookings")
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    selected_seats = models.CharField(
        max_length=255,
        help_text="Comma-separated seat codes, e.g. A1, A2, B5"
    )
    total_paid = models.DecimalField(max_digits=8, decimal_places=2)
    booking_code = models.CharField(max_length=32, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.booking_code:
            self.booking_code = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_code} - {self.customer_name} ({self.selected_seats})"

    def seats_list(self):
        if not self.selected_seats:
            return []
        return [s.strip().upper() for s in self.selected_seats.split(",") if s.strip()]

    @property
    def seat_count(self):
        return len(self.seats_list())


class MovieReview(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    reviewer_name = models.CharField(max_length=100)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating between 1 and 5 stars"
    )
    comment = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.reviewer_name} - {self.rating}★ for {self.movie.title}"
