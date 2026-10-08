import re
from decimal import Decimal
from django import forms
from .models import SeatBooking, MovieReview


VALID_ROWS = {"A", "B", "C", "D", "E"}
VALID_COLS = {str(i) for i in range(1, 9)}  # 1 to 8


class SeatBookingForm(forms.ModelForm):
    class Meta:
        model = SeatBooking
        fields = ["customer_name", "customer_email", "customer_phone", "selected_seats"]
        widgets = {
            "customer_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your full name",
                "required": True,
            }),
            "customer_email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "name@example.com",
                "required": True,
            }),
            "customer_phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "+1 (555) 000-1234",
                "required": True,
            }),
            "selected_seats": forms.HiddenInput(),
        }

    def __init__(self, *args, showtime=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.showtime = showtime

    def clean_selected_seats(self):
        seats_raw = self.cleaned_data.get("selected_seats", "").strip()
        if not seats_raw:
            raise forms.ValidationError("Please select at least one seat from the cinema grid.")

        seat_tokens = [s.strip().upper() for s in seats_raw.split(",") if s.strip()]
        if not seat_tokens:
            raise forms.ValidationError("Please select at least one valid seat.")

        # Check for duplicates in submission
        if len(seat_tokens) != len(set(seat_tokens)):
            raise forms.ValidationError("Duplicate seats detected in your selection.")

        # Validate that each seat is on the 5x8 grid (A-E, 1-8)
        for seat in seat_tokens:
            match = re.fullmatch(r"([A-E])([1-8])", seat)
            if not match:
                raise forms.ValidationError(f"Invalid seat code '{seat}'. Seats must be between A1 and E8.")

        return ", ".join(sorted(seat_tokens))

    def clean(self):
        cleaned_data = super().clean()
        selected_seats_str = cleaned_data.get("selected_seats")

        if not selected_seats_str or not self.showtime:
            return cleaned_data

        seat_tokens = [s.strip().upper() for s in selected_seats_str.split(",") if s.strip()]
        
        # Check against existing bookings for this showtime in the database
        booked_seats = set(self.showtime.get_booked_seats_list())
        conflicting = [s for s in seat_tokens if s in booked_seats]

        if conflicting:
            raise forms.ValidationError(
                f"Booking conflict: The following seat(s) are already booked: {', '.join(conflicting)}. "
                "Please select different seats."
            )

        # Calculate server-side total payment
        cleaned_data["calculated_total"] = Decimal(len(seat_tokens)) * self.showtime.ticket_price
        return cleaned_data


class MovieReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (5, "★★★★★ (5/5) - Masterpiece"),
        (4, "★★★★☆ (4/5) - Very Good"),
        (3, "★★★☆☆ (3/5) - Average"),
        (2, "★★☆☆☆ (2/5) - Below Average"),
        (1, "★☆☆☆☆ (1/5) - Poor"),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_rating"}),
        initial=5,
    )

    class Meta:
        model = MovieReview
        fields = ["reviewer_name", "rating", "comment"]
        widgets = {
            "reviewer_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Your name or nickname",
                "required": True,
            }),
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Share your thoughts about the movie...",
                "required": True,
            }),
        }

    def clean_rating(self):
        val = int(self.cleaned_data.get("rating", 5))
        if val < 1 or val > 5:
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return val
