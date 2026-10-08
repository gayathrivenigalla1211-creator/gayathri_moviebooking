from django.contrib import admin
from .models import Movie, Showtime, SeatBooking, MovieReview


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "formatted_duration", "release_date", "get_avg_rating", "get_reviews_count")
    list_filter = ("genre", "release_date")
    search_fields = ("title", "description", "genre")

    def get_avg_rating(self, obj):
        avg = obj.average_rating()
        return f"{avg} ★" if avg else "No ratings"
    get_avg_rating.short_description = "Avg Rating"

    def get_reviews_count(self, obj):
        return obj.review_count()
    get_reviews_count.short_description = "Reviews"


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ("movie", "show_date", "show_time", "screen_number", "ticket_price", "booked_seats_count")
    list_filter = ("show_date", "screen_number", "movie")
    search_fields = ("movie__title", "screen_number")

    def booked_seats_count(self, obj):
        booked = len(obj.get_booked_seats_list())
        return f"{booked} / {obj.total_seats} booked"
    booked_seats_count.short_description = "Occupancy"


@admin.register(SeatBooking)
class SeatBookingAdmin(admin.ModelAdmin):
    list_display = ("booking_code", "customer_name", "customer_email", "showtime", "selected_seats", "total_paid", "created_at")
    list_filter = ("showtime__show_date", "created_at")
    search_fields = ("booking_code", "customer_name", "customer_email", "customer_phone", "selected_seats")
    readonly_fields = ("booking_code", "created_at")


@admin.register(MovieReview)
class MovieReviewAdmin(admin.ModelAdmin):
    list_display = ("movie", "reviewer_name", "rating", "created_date", "short_comment")
    list_filter = ("rating", "created_date", "movie")
    search_fields = ("reviewer_name", "comment", "movie__title")

    def short_comment(self, obj):
        return obj.comment[:60] + "..." if len(obj.comment) > 60 else obj.comment
    short_comment.short_description = "Comment"
