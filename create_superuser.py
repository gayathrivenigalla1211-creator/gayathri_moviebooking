import os
import django
from datetime import date, time, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from movies.models import Movie, Showtime, SeatBooking, MovieReview

User = get_user_model()

def create_admin():
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@cineverse.com")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin123")

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully.")
    else:
        print(f"Superuser '{username}' already exists.")

def seed_sample_data():
    if Movie.objects.exists():
        print("Database already contains movies. Skipping seed.")
        return

    print("Seeding initial movies, showtimes, reviews and bookings...")

    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)

    movies_data = [
        {
            "title": "Interstellar: Beyond Time",
            "genre": "Sci-Fi",
            "duration": 169,
            "release_date": date(2024, 11, 7),
            "poster_url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=600&auto=format&fit=crop&q=80",
            "description": "When Earth becomes uninhabitable, a team of intrepid astronauts embarks on a dangerous journey through a wormhole across the galaxy to find a new home for mankind.",
            "showtimes": [
                {"date": today, "time": time(14, 30), "price": 14.50, "screen": "Screen 1 (IMAX Laser)"},
                {"date": today, "time": time(18, 0), "price": 16.00, "screen": "Screen 1 (IMAX Laser)"},
                {"date": tomorrow, "time": time(15, 15), "price": 14.50, "screen": "Screen 2 (Dolby Atmos)"},
                {"date": tomorrow, "time": time(20, 30), "price": 16.00, "screen": "Screen 1 (IMAX Laser)"},
            ],
            "reviews": [
                {"name": "Elena Rostova", "rating": 5, "comment": "A breathtaking cinematic masterpiece! The docking scene and soundtrack left me breathless."},
                {"name": "Marcus Vance", "rating": 5, "comment": "Emotional, scientifically thought-provoking, and visual grandeur at its finest."},
                {"name": "Chloe Bennett", "rating": 4, "comment": "Incredible sound engineering and visuals. A bit dense in the third act but totally rewarding."},
            ]
        },
        {
            "title": "Dune: Part Two",
            "genre": "Sci-Fi",
            "duration": 166,
            "release_date": date(2024, 3, 1),
            "poster_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop&q=80",
            "description": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family. Facing a choice between love and the fate of the universe.",
            "showtimes": [
                {"date": today, "time": time(16, 0), "price": 15.00, "screen": "Screen 2 (Dolby Atmos)"},
                {"date": today, "time": time(20, 0), "price": 15.00, "screen": "Screen 2 (Dolby Atmos)"},
                {"date": tomorrow, "time": time(17, 45), "price": 15.00, "screen": "Screen 3 (VIP)"},
            ],
            "reviews": [
                {"name": "David Thorne", "rating": 5, "comment": "Pure cinematic perfection. Denis Villeneuve delivers one of the greatest sci-fi epics of our generation."},
                {"name": "Amina K.", "rating": 5, "comment": "The worm riding sequence on IMAX was thunderous! Austin Butler was terrifyingly captivating."},
            ]
        },
        {
            "title": "Oppenheimer",
            "genre": "Drama",
            "duration": 180,
            "release_date": date(2023, 7, 21),
            "poster_url": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=600&auto=format&fit=crop&q=80",
            "description": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II.",
            "showtimes": [
                {"date": today, "time": time(13, 0), "price": 13.50, "screen": "Screen 3 (VIP)"},
                {"date": tomorrow, "time": time(19, 0), "price": 14.50, "screen": "Screen 1 (IMAX Laser)"},
                {"date": day_after, "time": time(14, 0), "price": 13.50, "screen": "Screen 2 (Dolby Atmos)"},
            ],
            "reviews": [
                {"name": "Sophia Zhang", "rating": 5, "comment": "Cillian Murphy gives the performance of a lifetime. The tension during the Trinity test is unforgettable."},
                {"name": "Liam Gallagher", "rating": 4, "comment": "Intense, philosophical, and brilliantly edited. Deserves all the accolades."},
            ]
        },
        {
            "title": "Spider-Man: Across the Spider-Verse",
            "genre": "Animation",
            "duration": 140,
            "release_date": date(2023, 6, 2),
            "poster_url": "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=600&auto=format&fit=crop&q=80",
            "description": "Miles Morales catapults across the Multiverse, where he encounters a team of Spider-People charged with protecting its very existence.",
            "showtimes": [
                {"date": today, "time": time(12, 0), "price": 12.00, "screen": "Screen 1 (IMAX Laser)"},
                {"date": today, "time": time(15, 0), "price": 12.00, "screen": "Screen 3 (VIP)"},
                {"date": tomorrow, "time": time(13, 30), "price": 12.00, "screen": "Screen 1 (IMAX Laser)"},
            ],
            "reviews": [
                {"name": "Jordan Reed", "rating": 5, "comment": "Every single frame is a museum-worthy work of art. The animation styles blend seamlessly."},
                {"name": "Maya Patel", "rating": 5, "comment": "Gwen's dimension colors shifting with emotion was legendary. Can't wait for Beyond the Spider-Verse!"},
            ]
        },
        {
            "title": "The Dark Knight",
            "genre": "Action",
            "duration": 152,
            "release_date": date(2024, 8, 15),
            "poster_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600&auto=format&fit=crop&q=80",
            "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
            "showtimes": [
                {"date": tomorrow, "time": time(18, 30), "price": 14.00, "screen": "Screen 2 (Dolby Atmos)"},
                {"date": tomorrow, "time": time(21, 45), "price": 14.00, "screen": "Screen 2 (Dolby Atmos)"},
            ],
            "reviews": [
                {"name": "Rachel Zane", "rating": 5, "comment": "Heath Ledger's Joker will never be topped. Pure perfection from start to finish."},
            ]
        },
        {
            "title": "Cyberpunk: Neon Genesis",
            "genre": "Action",
            "duration": 135,
            "release_date": date(2024, 10, 1),
            "poster_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop&q=80",
            "description": "In a sprawling mega-city governed by artificial intelligence, a rogue neural hacker discovers a clandestine synthetic uprising.",
            "showtimes": [
                {"date": today, "time": time(21, 30), "price": 13.00, "screen": "Screen 3 (VIP)"},
                {"date": tomorrow, "time": time(22, 0), "price": 13.00, "screen": "Screen 3 (VIP)"},
            ],
            "reviews": [
                {"name": "Kenji Sato", "rating": 4, "comment": "Super stylish neon-noir thriller with pulsating electronic beats and mind-bending action."},
            ]
        }
    ]

    for m_data in movies_data:
        movie = Movie.objects.create(
            title=m_data["title"],
            genre=m_data["genre"],
            duration=m_data["duration"],
            release_date=m_data["release_date"],
            poster_url=m_data["poster_url"],
            description=m_data["description"],
        )

        # Create showtimes
        created_showtimes = []
        for st_data in m_data["showtimes"]:
            st = Showtime.objects.create(
                movie=movie,
                show_date=st_data["date"],
                show_time=st_data["time"],
                ticket_price=st_data["price"],
                screen_number=st_data["screen"],
            )
            created_showtimes.append(st)

        # Create reviews
        for rev_data in m_data["reviews"]:
            MovieReview.objects.create(
                movie=movie,
                reviewer_name=rev_data["name"],
                rating=rev_data["rating"],
                comment=rev_data["comment"],
            )

        # Seed sample booking on the first showtime so some seats are visibly reserved
        if created_showtimes:
            first_st = created_showtimes[0]
            SeatBooking.objects.create(
                showtime=first_st,
                customer_name="Demo Customer",
                customer_email="demo@cineverse.com",
                customer_phone="+1 (555) 234-5678",
                selected_seats="C4, C5",
                total_paid=first_st.ticket_price * 2,
            )

    print("Sample movie records and showtimes seeded successfully!")

if __name__ == "__main__":
    create_admin()
    seed_sample_data()
