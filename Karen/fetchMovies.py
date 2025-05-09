# import requests
# import os
# from dotenv import load_dotenv

# # Load API Key from .env file
# load_dotenv()
# TMDB_API_KEY = os.getenv("TMDB_API_KEY")
# TMDB_MOVIE_URL = "https://api.themoviedb.org/3/discover/movie"

# # A dictionary to hold user states
# user_states = {}

# # TMDB Genre ID Mapping
# GENRE_MAPPING = {
#     "action": 28, "adventure": 12, "animation": 16, "comedy": 35, "crime": 80,
#     "documentary": 99, "drama": 18, "family": 10751, "fantasy": 14, "history": 36,
#     "horror": 27, "music": 10402, "mystery": 9648, "romance": 10749, "sci-fi": 878,
#     "thriller": 53, "war": 10752, "western": 37
# }

# def fetch_from_tmdb(pages=5):
#     """Fetch top movies from TMDB API across multiple pages."""
#     try:
#         all_movies = []
#         for page in range(1, pages + 1):
#             params = {
#                 "api_key": TMDB_API_KEY,
#                 "language": "en-US",
#                 "sort_by": "popularity.desc",
#                 "include_adult": False,
#                 "include_video": False,
#                 "page": page
#             }
#             response = requests.get(TMDB_MOVIE_URL, params=params)
#             response.raise_for_status()  # Raises error for HTTP failures
#             data = response.json()
#             movies = data.get("results", [])
            
#             if not movies:
#                 break  # Stop if no movies on this page

#             all_movies.extend(movies)

#         return all_movies  # List of movies

#     except Exception as e:
#         print(f"❌ TMDB API Error: {e}")
#         return []  # Return empty list if error occurs

# async def fetchMovies(preferred_genre, disliked_genres, message, user_id):
#     """Fetch movies from TMDB API and filter based on user preferences."""
#     try:
#         movies = fetch_from_tmdb()  # Fetch top movies

#         if not movies:  # If empty list returned, means API error
#             await message.channel.send("⚠️ **Error fetching movies. Please try again later.**")
#             return

#         total_movies = len(movies)  # Total fetched movies
        
#         # ✅ Get genre ID for preferred genre
#         preferred_genre_id = GENRE_MAPPING.get(preferred_genre.lower())

#         if not preferred_genre_id:
#             await message.channel.send("❌ **Invalid genre! Try again.**")
#             return

#         # ✅ Convert disliked genres to IDs
#         disliked_genre_ids = {GENRE_MAPPING[g.lower()] for g in disliked_genres if g.lower() in GENRE_MAPPING}

#         # ✅ Filter movies based on preferred genre
#         filtered_movies = [
#             movie for movie in movies if preferred_genre_id in movie.get('genre_ids', [])
#         ]

#         # ✅ Remove movies that contain any disliked genre
#         if disliked_genre_ids:
#             filtered_movies = [
#                 movie for movie in filtered_movies if not any(
#                     genre in disliked_genre_ids for genre in movie.get("genre_ids", [])
#                 )
#             ]

#         filtered_count = len(filtered_movies)  # Number of filtered movies

#         # ✅ Store filtered list for later use
#         user_states[f"{user_id}_filtered_movies"] = filtered_movies

#         # ✅ Notify user and ask how many movies they want
#         await message.channel.send(
#             f"\n📡 **Fetching fresh movies from Online...**\n"
#             f"✅ **I got the top {total_movies} movies based on your preferences.**\n"
#             f"⏳ Others will take more time as the server is busy.\n"
#             f"🎬 **There are {filtered_count} {preferred_genre.lower()} movies selected based on your preferences.**\n\n"
#             f"👉 **How many {preferred_genre.lower()} movies do you want to see?**"
#         )

#         # ✅ Update state for user to enter movie count
#         user_states[user_id] = {
#             "status": "awaiting_movie_count",
#             "available_movies": filtered_count
#         }

#     except Exception as e:
#         print(f"❌ Error fetching movies: {e}")
#         await message.channel.send("⚠️ **Error fetching movies. Please try again later.**")



import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CACHE_FILE = "movies_cache.json"
user_states = {}

# TMDB Genre Mapping
GENRE_MAPPING = {
    "action": 28, "adventure": 12, "animation": 16, "comedy": 35, "crime": 80,
    "documentary": 99, "drama": 18, "family": 10751, "fantasy": 14, "history": 36,
    "horror": 27, "music": 10402, "mystery": 9648, "romance": 10749, "sci-fi": 878,
    "thriller": 53, "war": 10752, "western": 37
}

def fetch_from_tmdb():
    """Load cached movie data from JSON."""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as file:
                return json.load(file)
        else:
            print("⚠️ movies_cache.json not found.")
            return []
    except Exception as e:
        print(f"❌ Error reading cached movie file: {e}")
        return []

async def fetchMovies(preferred_genres, disliked_genres, message, user_id, moods=None, disliked_moods=None):
    """
    Filter cached movies by preferred/disliked genres and moods.
    """
    try:
        movies = fetch_from_tmdb()

        if not movies:
            await message.channel.send("⚠️ **No cached movies found. Please make sure `movies_cache.json` exists.**")
            return []

        total_movies = len(movies)

        # Show samples for debug
        print("\n=== Sample Movies from Cache ===")
        for i, movie in enumerate(movies[:3]):
            title = movie.get("title", "Unknown Title")
            genres = movie.get("genre_ids", [])
            print(f"{i+1}. {title} → genre_ids: {genres}")

        # Debug incoming filters
        print("\n=== DEBUG: Incoming filter values ===")
        print("Preferred Genres (raw):", preferred_genres)
        print("Disliked Genres (raw):", disliked_genres)
        print("Moods:", moods)
        print("Disliked Moods:", disliked_moods)
        print("Total Movies in Cache:", total_movies)

        # Convert genres to IDs
        preferred_genre_ids = [
            GENRE_MAPPING[g.strip().lower()] for g in preferred_genres if g.strip().lower() in GENRE_MAPPING
        ]
        disliked_genre_ids = {
            GENRE_MAPPING[g.strip().lower()] for g in disliked_genres if g.strip().lower() in GENRE_MAPPING
        }

        print("Resolved Preferred Genre IDs:", preferred_genre_ids)

        # Debug: Show how many movies have comedy (for test)
        comedy_count = sum(35 in movie.get("genre_ids", []) for movie in movies)
        print(f"📊 Comedy Movies in Cache: {comedy_count}")

        if not preferred_genre_ids:
            await message.channel.send("❌ **Invalid or missing preferred genres. Please try again.**")
            return []

        # Step 1: Filter by preferred genres (ANY match)
        filtered_movies = []
        for movie in movies:
            genre_ids = movie.get("genre_ids", [])
            if any(gid in genre_ids for gid in preferred_genre_ids):
                filtered_movies.append(movie)

        print("✅ Movies after preferred genre filtering:", len(filtered_movies))

        # Step 2: Filter out by disliked genres
        if disliked_genre_ids:
            filtered_movies = [
                movie for movie in filtered_movies
                if not any(gid in movie.get("genre_ids", []) for gid in disliked_genre_ids)
            ]
            print("✅ Movies after removing disliked genres:", len(filtered_movies))

        # Step 3: Filter by moods (overview-based)
        if moods:
            moods = [m.lower().strip() for m in moods]
            filtered_movies = [
                movie for movie in filtered_movies
                if any(mood in movie.get("overview", "").lower() for mood in moods)
            ]
            print("✅ Movies after preferred mood filtering:", len(filtered_movies))

        # Step 4: Remove disliked moods
        if disliked_moods:
            disliked_moods = [m.lower().strip() for m in disliked_moods]
            filtered_movies = [
                movie for movie in filtered_movies
                if not any(mood in movie.get("overview", "").lower() for mood in disliked_moods)
            ]
            print("✅ Movies after removing disliked moods:", len(filtered_movies))

        # Step 5: Fallback keyword-based search if nothing matched
        if len(filtered_movies) == 0 and preferred_genres:
            keywords = [g.strip().lower() for g in preferred_genres]
            fallback = [
                movie for movie in movies
                if any(kw in movie.get("overview", "").lower() for kw in keywords)
            ]
            if fallback:
                filtered_movies = fallback
                print(f"🟡 Fallback: Found {len(fallback)} movies by keyword in overview.")

        filtered_count = len(filtered_movies)

        user_states[f"{user_id}_filtered_movies"] = filtered_movies

        await message.channel.send(
            f"📦 **Using Karen's cached movie list...**\n"
            f"✅ **There are {total_movies} movies available.**\n"
            f"🎬 **Filtered {filtered_count} movies based on your preferences.**\n\n"
            f"👉 **How many movies would you like to see?**"
        )

        user_states[user_id] = {
            "status": "awaiting_movie_count",
            "available_movies": filtered_count
        }

        return filtered_movies

    except Exception as e:
        print(f"❌ Error in fetchMovies: {e}")
        await message.channel.send("⚠️ **Something went wrong while filtering. Please try again.**")
        return []
