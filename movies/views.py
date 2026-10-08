from collections import defaultdict
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Movie, Showtime, SeatBooking, MovieReview
from .forms import SeatBookingForm, MovieReviewForm


def movie_list(request):
    """Movie list page with search, genre filtering, and sorting."""
    query = request.GET.get("q", "").strip()
    selected_genre = request.GET.get("genre", "").strip()
    sort_by = request.GET.get("sort", "featured").strip()

    movies = Movie.objects.all()

    if query:
        movies = movies.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(genre__icontains=query)
        )

    if selected_genre:
        movies = movies.filter(genre__iexact=selected_genre)

    if sort_by == "rating":
        # Sort by average rating descending in python or annotate
        movies = sorted(movies, key=lambda m: (m.average_rating() or 0), reverse=True)
    elif sort_by == "newest":
        movies = movies.order_by("-release_date")
    elif sort_by == "title":
        movies = movies.order_by("title")
    else:
        # Default featured
        movies = movies.order_by("-release_date", "title")

    # Available genres for filter pills
    all_genres = [
        "Action", "Sci-Fi", "Drama", "Animation", "Comedy",
        "Thriller", "Horror", "Adventure", "Romance"
    ]

    context = {
        "movies": movies,
        "query": query,
        "selected_genre": selected_genre,
        "sort_by": sort_by,
        "all_genres": all_genres,
    }
    return render(request, "movies/movie_list.html", context)


def movie_detail(request, pk):
    """Movie detail page with organized showtimes, reviews list, and review form."""
    movie = get_object_or_404(Movie, pk=pk)
    review_form = MovieReviewForm()

    # Get showtimes grouped by date
    showtimes = movie.showtimes.all().order_by("show_date", "show_time")
    
    showtimes_by_date = defaultdict(list)
    for st in showtimes:
        showtimes_by_date[st.show_date].append(st)

    # Convert defaultdict to sorted list of tuples (date, list_of_showtimes)
    grouped_showtimes = sorted(showtimes_by_date.items(), key=lambda item: item[0])

    reviews = movie.reviews.all().order_by("-created_date")
    avg_rating = movie.average_rating()
    review_count = movie.review_count()

    # Star distribution calculations (1 to 5)
    rating_distribution = {i: 0 for i in range(1, 6)}
    if review_count > 0:
        for r in reviews:
            if 1 <= r.rating <= 5:
                rating_distribution[r.rating] += 1
        star_bars = []
        for star in range(5, 0, -1):
            count = rating_distribution[star]
            pct = round((count / review_count) * 100)
            star_bars.append({"star": star, "count": count, "percent": pct})
    else:
        star_bars = [{"star": star, "count": 0, "percent": 0} for star in range(5, 0, -1)]

    context = {
        "movie": movie,
        "grouped_showtimes": grouped_showtimes,
        "reviews": reviews,
        "review_form": review_form,
        "avg_rating": avg_rating,
        "review_count": review_count,
        "star_bars": star_bars,
    }
    return render(request, "movies/movie_detail.html", context)


def add_review(request, movie_id):
    """Handle 1-5 star movie review submission."""
    movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == "POST":
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.save()
            messages.success(request, f"Thank you, {review.reviewer_name}! Your {review.rating}-star review was posted successfully.")
            return redirect(f"/movies/{movie.id}/#reviews-section")
        else:
            messages.error(request, "Failed to submit review. Please check the fields and rating.")
            # Re-render movie detail with form errors
            showtimes = movie.showtimes.all().order_by("show_date", "show_time")
            showtimes_by_date = defaultdict(list)
            for st in showtimes:
                showtimes_by_date[st.show_date].append(st)
            grouped_showtimes = sorted(showtimes_by_date.items(), key=lambda item: item[0])
            reviews = movie.reviews.all().order_by("-created_date")

            return render(request, "movies/movie_detail.html", {
                "movie": movie,
                "grouped_showtimes": grouped_showtimes,
                "reviews": reviews,
                "review_form": form,
                "avg_rating": movie.average_rating(),
                "review_count": movie.review_count(),
            })

    return redirect("movies:movie_detail", pk=movie.id)


def seat_booking(request, showtime_id):
    """Interactive 5x8 seat selection and ticket booking workflow."""
    showtime = get_object_or_404(Showtime, pk=showtime_id)
    booked_seats = showtime.get_booked_seats_list()

    # Define 5x8 grid specification
    row_letters = ["A", "B", "C", "D", "E"]
    col_numbers = list(range(1, 9))

    # Pre-build seat grid state for template rendering
    grid_rows = []
    for row in row_letters:
        row_seats = []
        for col in col_numbers:
            seat_code = f"{row}{col}"
            row_seats.append({
                "code": seat_code,
                "row": row,
                "col": col,
                "is_booked": seat_code in booked_seats,
            })
        grid_rows.append({"row_name": row, "seats": row_seats})

    if request.method == "POST":
        form = SeatBookingForm(request.POST, showtime=showtime)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.showtime = showtime
            # Total payment calculated server-side
            booking.total_paid = form.cleaned_data["calculated_total"]
            booking.save()

            messages.success(request, f"Booking successful! Your ticket code is {booking.booking_code}.")
            return redirect("movies:booking_confirmation", booking_id=booking.id)
        else:
            # Add form error message
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = SeatBookingForm(showtime=showtime)

    context = {
        "showtime": showtime,
        "movie": showtime.movie,
        "grid_rows": grid_rows,
        "booked_seats": booked_seats,
        "form": form,
        "ticket_price": float(showtime.ticket_price),
    }
    return render(request, "movies/seat_booking.html", context)


def booking_confirmation(request, booking_id):
    """Cinema pass / ticket confirmation view with complete booking summary."""
    booking = get_object_or_404(SeatBooking, pk=booking_id)
    seats_list = booking.seats_list()

    context = {
        "booking": booking,
        "showtime": booking.showtime,
        "movie": booking.showtime.movie,
        "seats_list": seats_list,
    }
    return render(request, "movies/booking_confirmation.html", context)


def my_bookings(request):
    """Customer lookup page to view and print past bookings by email or ticket code."""
    query = request.GET.get("q", "").strip()
    bookings = []
    has_searched = False

    if query:
        has_searched = True
        bookings = SeatBooking.objects.filter(
            Q(customer_email__iexact=query) |
            Q(booking_code__iexact=query) |
            Q(customer_phone__iexact=query)
        ).order_by("-created_at")

    context = {
        "query": query,
        "bookings": bookings,
        "has_searched": has_searched,
    }
    return render(request, "movies/my_bookings.html", context)
