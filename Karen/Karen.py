# import os
# import discord
# import requests
# import json
# import re
# import google.generativeai as genai
# from dotenv import load_dotenv
# from fetchMovies import fetchMovies, GENRE_MAPPING

# # Load API keys from .env file
# load_dotenv()
# KarenDiscord = os.getenv("KAREN_GEMINI_DISCORD")
# TMDB_API_KEY = os.getenv("TMDB_API_KEY")
# GOOGLE_API_KEY = os.getenv("KAREN_GEMINI")

# # Configure Gemini API
# genai.configure(api_key=GOOGLE_API_KEY)

# intents = discord.Intents.default()
# intents.messages = True
# intents.message_content = True
# client = discord.Client(intents=intents)
# user_states = {}

# MOODS = {
#     "fast-paced": ["action-packed", "intense", "high-energy"],
#     "slow": ["calm", "leisurely", "steady"],
#     "thoughtful": ["deep", "philosophical", "insightful"],
#     "emotional": ["heartfelt", "moving", "tearjerker"],
#     "relaxing": ["chill", "easygoing", "soothing"],
#     "thrilling": ["suspenseful", "exciting", "edge-of-seat"]
# }

# def get_genres():
#     url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
#     response = requests.get(url)
#     if response.status_code == 200:
#         genres = response.json().get("genres", [])
#         return {genre["name"].lower(): genre["id"] for genre in genres}
#     return {}

# GENRE_DICT = get_genres()

# def analyze_preferences(user_input):
#     model = genai.GenerativeModel("gemini-2.0-flash")
#     prompt = f'''
#     Extract movie preferences from the user's message. Identify:
#     - Preferred genres (if mentioned, else omit them)
#     - Disliked genres (if mentioned, else omit them)
#     - Mood (if mentioned, else omit it)

#     User's Message: "{user_input}"

#     Reply in JSON format:
#     {{
#         "preferred_genres": ["Extracted preferred genres (if any, else omit)"],
#         "disliked_genres": ["Extracted disliked genres (if any, else omit)"],
#         "mood": "Extracted mood (if any, else omit)"
#     }}
#     '''
#     try:
#         response = model.generate_content(prompt)
#         if response and response.text.strip():
#             try:
#                 return json.loads(response.text)
#             except json.JSONDecodeError:
#                 pass
#         json_match = re.search(r'\{.*\}', response.text.strip(), re.DOTALL)
#         if json_match:
#             return json.loads(json_match.group())
#         return {}
#     except Exception as e:
#         print(f"❌ Error parsing Gemini response: {e}")
#         return {}

# def get_closest_mood(user_input):
#     for mood, synonyms in MOODS.items():
#         if user_input.lower() in [mood] + synonyms:
#             return mood
#     return None

# @client.event
# async def on_ready():
#     print(f"Bot is online as {client.user}")

# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

#     user_id = message.author.id

#     if message.content.lower() == "hello":
#         await message.channel.send("Hey there! 😊 Ready to find a great movie? \n(Reply with 'yeah', 'yes', or 'yo' to continue, or 'no' to exit)")
#         user_states[user_id] = "awaiting_confirmation"

#     elif user_states.get(user_id) == "awaiting_confirmation":
#         if message.content.lower() in ["yeah", "yes", "yo"]:
#             if not GENRE_DICT:
#                 await message.channel.send("❌ Unable to fetch genres. Please try again later.")
#                 return
#             genre_list = "\n".join([f"- {g.capitalize()}" for g in GENRE_DICT])
#             await message.channel.send(f"**🎬 Available Genres:**\n{genre_list}\n\n👉 Describe the kind of movies you like:")
#             user_states[user_id] = "awaiting_preferences"
#         elif message.content.lower() == "no":
#             await message.channel.send("Alright, no worries! Have a great day! 😊")
#             user_states.pop(user_id, None)

#     elif user_states.get(user_id) == "awaiting_preferences":
#         preferences = analyze_preferences(message.content)
#         preferred_genres = preferences.get("preferred_genres", [])
#         preferred_genres = [g.lower() for g in preferred_genres if isinstance(g, str)]

#         disliked_genres = preferences.get("disliked_genres", []) if isinstance(preferences.get("disliked_genres"), list) else []
#         mood = preferences.get("mood", "").lower() if isinstance(preferences.get("mood"), str) else ""

#         valid_disliked_genres = [dg for dg in disliked_genres if dg in GENRE_DICT]

#         if not preferred_genres:
#             await message.channel.send("❌ Please specify at least one genre you like.")
#             return

#         if not valid_disliked_genres:
#             await message.channel.send("🤔 Do you want to continue without a Disliked Genre? (yes/no):")
#             user_states[user_id] = "awaiting_disliked_confirmation"
#             user_states[f"{user_id}_preferred_genres"] = preferred_genres
#             return

#         user_states[user_id] = "awaiting_mood"
#         user_states[f"{user_id}_preferred_genres"] = preferred_genres
#         user_states[f"{user_id}_disliked_genres"] = valid_disliked_genres
#         await message.channel.send("\n🎭 Available Moods: " + ", ".join(MOODS.keys()) + "\n\n🤔 Do you want to continue without selecting a Mood? (yes/no):")

#     elif user_states.get(user_id) == "awaiting_disliked_confirmation":
#         if message.content.lower() == "yes":
#             user_states[user_id] = "awaiting_mood"
#             await message.channel.send("🎭 Available Moods: " + ", ".join(MOODS.keys()) + "\n\n🤔 Do you want to continue without selecting a Mood? (yes/no):")
#         elif message.content.lower() == "no":
#             await message.channel.send("👉 Enter genres you dislike (comma-separated):")
#             user_states[user_id] = "awaiting_disliked_genres"

#     elif user_states.get(user_id) == "awaiting_disliked_genres":
#         disliked_genres_input = message.content.lower().split(",")
#         valid_disliked_genres = [g.strip() for g in disliked_genres_input if g.strip() in GENRE_DICT]
#         user_states[f"{user_id}_disliked_genres"] = valid_disliked_genres
#         user_states[user_id] = "awaiting_mood"
#         await message.channel.send("🎭 Available Moods: " + ", ".join(MOODS.keys()) + "\n\n🤔 Do you want to continue without selecting a Mood? (yes/no):")

#     elif user_states.get(user_id) == "awaiting_mood":
#         mood = None
#         if message.content.lower() != "yes":
#             mood = get_closest_mood(message.content)
#             if not mood:
#                 await message.channel.send("❌ Invalid mood. Please choose from the available moods.")
#                 return

#         preferred_genres = user_states.get(f"{user_id}_preferred_genres", [])
#         disliked_genres = user_states.get(f"{user_id}_disliked_genres", [])

#         if not preferred_genres:
#             await message.channel.send("❌ Error: Preferred genres missing. Please restart.")
#             return

#         msg = f"**🎬 Extracted Preferences:**\n✅ **Preferred Genres:** {', '.join(preferred_genres)}\n"
#         if disliked_genres:
#             msg += f"❌ **Disliked Genres:** {', '.join(disliked_genres)}\n"
#         if mood:
#             msg += f"🎭 **Mood:** {mood.capitalize()}"
#         await message.channel.send(msg)

#         filtered_movies = await fetchMovies(preferred_genres, disliked_genres, message, user_id)

#         if not filtered_movies:
#             return

#         user_states[f"{user_id}_filtered_movies"] = filtered_movies
#         user_states[user_id] = "awaiting_movie_count"

#     elif user_states.get(user_id) == "awaiting_movie_count":
#         try:
#             movie_count = int(message.content.strip())
#             filtered_movies = user_states.get(f"{user_id}_filtered_movies", [])

#             if not filtered_movies:
#                 await message.channel.send("⚠️ No movies found. Please try again.")
#                 return

#             movie_count = min(movie_count, len(filtered_movies))
#             selected_movies = filtered_movies[:movie_count]

#             await message.channel.send(f"📽️ **Here are your {movie_count} movies:**")
#             chunk = ""
#             max_len = 1900

#             for i, movie in enumerate(selected_movies, start=1):
#                 title = movie.get('title', 'Unknown Title')
#                 overview = movie.get('overview', 'No description available.')
#                 entry = f"\n{i} **{title}**\n📖 {overview.strip()}\n"
#                 if len(chunk) + len(entry) > max_len:
#                     await message.channel.send(chunk)
#                     chunk = entry
#                 else:
#                     chunk += entry

#             if chunk.strip():
#                 await message.channel.send(chunk)

#             del user_states[user_id]
#             del user_states[f"{user_id}_filtered_movies"]

#         except ValueError:
#             await message.channel.send("❌ Please enter a valid number.")

# # Start the bot
# client.run(KarenDiscord)


































# import os
# import discord
# import requests
# import json
# import re
# import google.generativeai as genai
# from dotenv import load_dotenv
# from fetchMovies import fetchMovies, GENRE_MAPPING

# # Load API keys from .env file
# load_dotenv()
# KarenDiscord = os.getenv("KAREN_GEMINI_DISCORD")
# TMDB_API_KEY = os.getenv("TMDB_API_KEY")
# GOOGLE_API_KEY = os.getenv("KAREN_GEMINI")

# # Configure Gemini API
# genai.configure(api_key=GOOGLE_API_KEY)

# intents = discord.Intents.default()
# intents.messages = True
# intents.message_content = True
# client = discord.Client(intents=intents)
# user_states = {}

# MOODS = {
#     "fast-paced": ["action-packed", "intense", "high-energy"],
#     "slow": ["calm", "leisurely", "steady"],
#     "thoughtful": ["deep", "philosophical", "insightful"],
#     "emotional": ["heartfelt", "moving", "tearjerker"],
#     "relaxing": ["chill", "easygoing", "soothing"],
#     "thrilling": ["suspenseful", "exciting", "edge-of-seat"]
# }

# def get_genres():
#     url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
#     response = requests.get(url)
#     if response.status_code == 200:
#         genres = response.json().get("genres", [])
#         return {genre["name"].lower(): genre["id"] for genre in genres}
#     return {}

# GENRE_DICT = get_genres()

# def analyze_preferences(user_input):
#     model = genai.GenerativeModel("gemini-2.0-flash")
#     prompt = f'''
#     Extract movie preferences from the user's message. Identify:
#     - Preferred genres (if mentioned, else omit them)
#     - Disliked genres (if mentioned, else omit them)
#     - Mood keywords (if mentioned, else omit them)

#     User's Message: "{user_input}"

#     Reply in JSON format:
#     {{
#         "preferred_genres": ["Extracted preferred genres (if any, else omit)"],
#         "disliked_genres": ["Extracted disliked genres (if any, else omit)"],
#         "moods": ["Extracted mood(s) (if any, else omit)"]
#     }}
#     '''
#     try:
#         response = model.generate_content(prompt)
#         if response and response.text.strip():
#             try:
#                 return json.loads(response.text)
#             except json.JSONDecodeError:
#                 pass
#         json_match = re.search(r'\{.*\}', response.text.strip(), re.DOTALL)
#         if json_match:
#             return json.loads(json_match.group())
#         return {}
#     except Exception as e:
#         print(f"❌ Error parsing Gemini response: {e}")
#         return {}

# def get_matching_moods(mood_list):
#     matched = []
#     for user_mood in mood_list:
#         for mood, synonyms in MOODS.items():
#             if user_mood in [mood] + synonyms:
#                 matched.append(mood)
#                 break
#     return list(set(matched))

# @client.event
# async def on_ready():
#     print(f"Bot is online as {client.user}")

# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

#     user_id = message.author.id

#     if message.content.lower() == "hello":
#         await message.channel.send("Hey there! 😊 Ready to find a great movie? \n(Reply with 'yeah', 'yes', or 'yo' to continue, or 'no' to exit)")
#         user_states[user_id] = "awaiting_confirmation"

#     elif user_states.get(user_id) == "awaiting_confirmation":
#         if message.content.lower() in ["yeah", "yes", "yo"]:
#             if not GENRE_DICT:
#                 await message.channel.send("❌ Unable to fetch genres. Please try again later.")
#                 return
#             genre_list = "\n".join([f"- {g.capitalize()}" for g in GENRE_DICT])
#             await message.channel.send(
#                 f"**🎬 Available Genres:**\n{genre_list}\n\n"
#                 "👉 Describe the kind of movies you like (e.g., `I love sci-fi but hate romance and slow movies.`):"
#             )
#             user_states[user_id] = "awaiting_preferences"
#         elif message.content.lower() == "no":
#             await message.channel.send("Alright, no worries! Have a great day! 😊")
#             user_states.pop(user_id, None)

#     elif user_states.get(user_id) == "awaiting_preferences":
#         preferences = analyze_preferences(message.content)
#         preferred_genres = preferences.get("preferred_genres", [])
#         preferred_genres = [g.lower() for g in preferred_genres if isinstance(g, str)]

#         disliked_genres = preferences.get("disliked_genres", []) if isinstance(preferences.get("disliked_genres"), list) else []
#         disliked_genres = [d.lower() for d in disliked_genres if isinstance(d, str)]

#         moods_raw = preferences.get("moods", []) if isinstance(preferences.get("moods"), list) else []
#         moods = [m.lower() for m in moods_raw if isinstance(m, str)]
#         matched_moods = get_matching_moods(moods)

#         valid_disliked_genres = [dg for dg in disliked_genres if dg in GENRE_DICT]

#         if not preferred_genres:
#             await message.channel.send("❌ Please specify at least one genre you like.")
#             return
#         if not matched_moods:
#             await message.channel.send("🤔 Do you want to continue without selecting a Mood? (yes/no):")
#             user_states[user_id] = "awaiting_mood"
#         else:
#             # Store everything and skip asking for mood again
#             user_states[f"{user_id}_preferred_genres"] = preferred_genres
#             user_states[f"{user_id}_disliked_genres"] = valid_disliked_genres
#             user_states[f"{user_id}_moods"] = matched_moods
#             user_states[user_id] = "awaiting_movie_count"

#             msg = f"**🎬 Extracted Preferences:**\n✅ **Preferred Genres:** {', '.join(preferred_genres)}\n"
#             if valid_disliked_genres:
#                 msg += f"❌ **Disliked Genres:** {', '.join(valid_disliked_genres)}\n"
#             msg += f"🎭 **Mood(s):** {', '.join(m.capitalize() for m in matched_moods)}\n"

#             await message.channel.send(msg)

#             filtered_movies = await fetchMovies(preferred_genres, valid_disliked_genres, message, user_id)

#             if not filtered_movies:
#                 return

#             user_states[f"{user_id}_filtered_movies"] = filtered_movies
#             user_states[user_id] = "awaiting_movie_count"


#         if not valid_disliked_genres:
#             await message.channel.send("🤔 Do you want to continue without a Disliked Genre? (yes/no):")
#             user_states[user_id] = "awaiting_disliked_confirmation"
#             user_states[f"{user_id}_preferred_genres"] = preferred_genres
#             user_states[f"{user_id}_moods"] = matched_moods
#             return

#         user_states[user_id] = "awaiting_mood"
#         user_states[f"{user_id}_preferred_genres"] = preferred_genres
#         user_states[f"{user_id}_disliked_genres"] = valid_disliked_genres
#         user_states[f"{user_id}_moods"] = matched_moods
#         await message.channel.send("\n🎭 Available Moods (you can list more than one): " + ", ".join(MOODS.keys()) + "\n\n🤔 Do you want to continue without selecting a Mood? (yes/no):")

#     elif user_states.get(user_id) == "awaiting_disliked_confirmation":
#         if message.content.lower() == "yes":
#             user_states[user_id] = "awaiting_mood"
#             await message.channel.send("🎭 Available Moods (you can list more than one): " + ", ".join(MOODS.keys()) + "\n\n🤔 Do you want to continue without selecting a Mood? (yes/no):")
#         elif message.content.lower() == "no":
#             await message.channel.send("👉 Enter genres you dislike (comma-separated):")
#             user_states[user_id] = "awaiting_disliked_genres"

#     elif user_states.get(user_id) == "awaiting_disliked_genres":
#         disliked_genres_input = message.content.lower().split(",")
#         valid_disliked_genres = [g.strip() for g in disliked_genres_input if g.strip() in GENRE_DICT]
#         user_states[f"{user_id}_disliked_genres"] = valid_disliked_genres
#         user_states[user_id] = "awaiting_mood"
#         await message.channel.send("🎭 Available Moods (you can list more than one): " + ", ".join(MOODS.keys()) + "\n\n🤔 Do you want to continue without selecting a Mood? (yes/no):")

#     elif user_states.get(user_id) == "awaiting_mood":
#         matched_moods = []
#         if message.content.lower() != "yes":
#             # 🔄 Replace this manual parsing:
#             # moods_input = message.content.lower().split(",")
#             # matched_moods = get_matching_moods([m.strip() for m in moods_input])

#             # ✅ Use Gemini to extract moods from full sentence input
#             preferences = analyze_preferences(message.content)
#             moods_raw = preferences.get("moods", []) if isinstance(preferences.get("moods"), list) else []
#             moods = [m.lower() for m in moods_raw if isinstance(m, str)]
#             matched_moods = get_matching_moods(moods)

#             if not matched_moods:
#                 await message.channel.send("❌ I couldn’t match any moods. Please choose from: " + ", ".join(MOODS.keys()))
#                 return


#         preferred_genres = user_states.get(f"{user_id}_preferred_genres", [])
#         disliked_genres = user_states.get(f"{user_id}_disliked_genres", [])

#         if not preferred_genres:
#             await message.channel.send("❌ Error: Preferred genres missing. Please restart.")
#             return

#         user_states[f"{user_id}_moods"] = matched_moods

#         msg = f"**🎬 Extracted Preferences:**\n✅ **Preferred Genres:** {', '.join(preferred_genres)}\n"
#         if disliked_genres:
#             msg += f"❌ **Disliked Genres:** {', '.join(disliked_genres)}\n"
#         if matched_moods:
#             msg += f"🎭 **Mood(s):** {', '.join(m.capitalize() for m in matched_moods)}\n"

#         await message.channel.send(msg)

#         filtered_movies = await fetchMovies(preferred_genres, disliked_genres, message, user_id)

#         if not filtered_movies:
#             return

#         user_states[f"{user_id}_filtered_movies"] = filtered_movies
#         user_states[user_id] = "awaiting_movie_count"

#     elif user_states.get(user_id) == "awaiting_movie_count":
#         try:
#             movie_count = int(message.content.strip())
#             filtered_movies = user_states.get(f"{user_id}_filtered_movies", [])

#             if not filtered_movies:
#                 await message.channel.send("⚠️ No movies found. Please try again.")
#                 return

#             movie_count = min(movie_count, len(filtered_movies))
#             selected_movies = filtered_movies[:movie_count]

#             await message.channel.send(f"📽️ **Here are your {movie_count} movies:**")
#             chunk = ""
#             max_len = 1900

#             for i, movie in enumerate(selected_movies, start=1):
#                 title = movie.get('title', 'Unknown Title')
#                 overview = movie.get('overview', 'No description available.')
#                 entry = f"\n{i} **{title}**\n📖 {overview.strip()}\n"
#                 if len(chunk) + len(entry) > max_len:
#                     await message.channel.send(chunk)
#                     chunk = entry
#                 else:
#                     chunk += entry

#             if chunk.strip():
#                 await message.channel.send(chunk)

#             del user_states[user_id]
#             del user_states[f"{user_id}_filtered_movies"]

#         except ValueError:
#             await message.channel.send("❌ Please enter a valid number.")

# # Start the bot
# client.run(KarenDiscord)












































import os
import discord
import requests
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
from fetchMovies import fetchMovies, GENRE_MAPPING
from pathlib import Path

load_dotenv(dotenv_path=Path('.') / '.env')

# Load API keys from .env file
# load_dotenv()
KarenDiscord = os.getenv("KAREN_GEMINI_DISCORD")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
GOOGLE_API_KEY = os.getenv("KAREN_GEMINI")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)
user_states = {}

MOODS = {
    "fast-paced": ["action-packed", "intense", "high-energy"],
    "slow": ["calm", "leisurely", "steady"],
    "thoughtful": ["deep", "philosophical", "insightful"],
    "emotional": ["heartfelt", "moving", "tearjerker"],
    "relaxing": ["chill", "easygoing", "soothing"],
    "thrilling": ["suspenseful", "exciting", "edge-of-seat"]
}

def get_genres():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        genres = response.json().get("genres", [])
        return {genre["name"].lower(): genre["id"] for genre in genres}
    return {}

GENRE_DICT = get_genres()

def analyze_preferences(user_input):
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f'''
    You are a helpful assistant designed to extract movie preferences from natural language input.

    Analyze the message and extract:
    - preferred_genres: genres the user says they like
    - disliked_genres: genres the user says they dislike
    - moods: desired movie moods (e.g., fast-paced, emotional, relaxing)
    - disliked_moods: moods the user wants to avoid

    🚫 Make sure NOT to include any disliked moods in the "moods" list.
    ✅ Accept sentences like "I don’t like slow movies", "Avoid emotional stories", "I prefer something intense"
    ✅ Support phrases like:
      - "I don’t like..."
      - "Avoid..."
      - "I’m tired of..."
      - "Select the rest"
      - "I prefer..."

    Examples:
    - Input: "I love sci-fi and comedy, but hate romance and slow movies"
      Output:
      {{
        "preferred_genres": ["sci-fi", "comedy"],
        "disliked_genres": ["romance"],
        "moods": [],
        "disliked_moods": ["slow"]
      }}

    - Input: "Not into emotional or romantic films. Give me something thrilling"
      Output:
      {{
        "preferred_genres": [],
        "disliked_genres": ["romance"],
        "moods": ["thrilling"],
        "disliked_moods": ["emotional"]
      }}

    User Message:
    "{user_input}"

    Return your response in pure JSON (no explanation, no markdown).
    '''

    try:
        response = model.generate_content(prompt)
        if response and response.text.strip():
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', response.text.strip(), re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        return {}
    except Exception as e:
        print(f"❌ Error parsing Gemini response: {e}")
        return {}

def get_matching_moods(mood_list):
    matched = []
    for user_mood in mood_list:
        for mood, synonyms in MOODS.items():
            if user_mood in [mood] + synonyms:
                matched.append(mood)
                break
    return list(set(matched))

@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_id = message.author.id

    if message.content.lower() == "hello":
        await message.channel.send("Hey there! 😊 Ready to find a great movie?\n(Reply with 'yeah', 'yes', or 'yo' to continue, or 'no' to exit)")
        user_states[user_id] = "awaiting_confirmation"

    elif user_states.get(user_id) == "awaiting_confirmation":
        if message.content.lower() in ["yeah", "yes", "yo"]:
            if not GENRE_DICT:
                await message.channel.send("❌ Unable to fetch genres. Please try again later.")
                return
            genre_list = "\n".join([f"- {g.capitalize()}" for g in GENRE_DICT])
            await message.channel.send(
                f"**🎬 Available Genres:**\n{genre_list}\n\n"
                "👉 Describe the kind of movies you like (e.g., `I love sci-fi but hate romance and slow movies`):"
            )
            user_states[user_id] = "awaiting_preferences"
        elif message.content.lower() == "no":
            await message.channel.send("Alright, no worries! Have a great day! 😊")
            user_states.pop(user_id, None)

    elif user_states.get(user_id) == "awaiting_preferences":
        preferences = analyze_preferences(message.content)
        preferred_genres = [g.lower() for g in preferences.get("preferred_genres", []) if isinstance(g, str)]
        disliked_genres = [d.lower() for d in preferences.get("disliked_genres", []) if isinstance(d, str)]
        moods_raw = preferences.get("moods", [])
        moods = [m.lower() for m in moods_raw if isinstance(m, str)]
        matched_moods = get_matching_moods(moods)
        # Handle disliked moods if present
        disliked_moods_raw = preferences.get("disliked_moods", []) if isinstance(preferences.get("disliked_moods"), list) else []
        disliked_moods = [m.lower() for m in disliked_moods_raw if isinstance(m, str)]
        matched_disliked = get_matching_moods(disliked_moods)

        # Remove disliked moods from matched moods
        matched_moods = [m for m in matched_moods if m not in matched_disliked]
        # Fallback: if no moods and user said "select the rest"
        if not matched_moods and "select the rest" in message.content.lower():
            all_moods = list(MOODS.keys())
            matched_moods = [m for m in all_moods if m not in matched_disliked]
        valid_disliked_genres = [dg for dg in disliked_genres if dg in GENRE_DICT]
        # if user_states.get(f"{user_id}_disliked_moods"):
        #     msg += f"🚫 **Disliked Moods:** {', '.join(user_states[f'{user_id}_disliked_moods'])}\n"

        if not preferred_genres:
            await message.channel.send("❌ Please specify at least one genre you like.")
            return

        # Save known values
        user_states[f"{user_id}_preferred_genres"] = preferred_genres
        user_states[f"{user_id}_disliked_moods"] = matched_disliked
        user_states[f"{user_id}_disliked_genres"] = valid_disliked_genres

        # Ask about missing values one-by-one
        if not valid_disliked_genres:
            await message.channel.send("🤔 Do you want to continue without a Disliked Genre? (yes/no):")
            user_states[user_id] = "awaiting_disliked_confirmation"
        elif not matched_moods:
            await message.channel.send("🤔 Do you want to continue without selecting a Mood? (yes/no):")
            user_states[user_id] = "awaiting_mood"
        else:
            await show_final_preferences_and_fetch(message, user_id)

    elif user_states.get(user_id) == "awaiting_disliked_confirmation":
        if message.content.lower() == "yes":
            if not user_states.get(f"{user_id}_moods"):
                await message.channel.send("🎭 Available Moods: " + ", ".join(MOODS.keys()) + "\n🤔 Do you want to continue without selecting a Mood? (yes/no):")
                user_states[user_id] = "awaiting_mood"
            else:
                await show_final_preferences_and_fetch(message, user_id)
        elif message.content.lower() == "no":
            await message.channel.send("👉 Enter genres you dislike (comma-separated):")
            user_states[user_id] = "awaiting_disliked_genres"

    elif user_states.get(user_id) == "awaiting_disliked_genres":
        disliked_input = [g.strip() for g in message.content.lower().split(",")]
        valid_disliked = [g for g in disliked_input if g in GENRE_DICT]
        user_states[f"{user_id}_disliked_genres"] = valid_disliked

        if not user_states.get(f"{user_id}_moods"):
            await message.channel.send("🎭 Available Moods: " + ", ".join(MOODS.keys()) + "\n🤔 Do you want to continue without selecting a Mood? (yes/no):")
            user_states[user_id] = "awaiting_mood"
        else:
            await show_final_preferences_and_fetch(message, user_id)

    elif user_states.get(user_id) == "awaiting_mood":
        if message.content.lower() != "yes":
            prefs = analyze_preferences(message.content)

            # Parse moods and disliked_moods
            moods_raw = prefs.get("moods", [])
            moods = [m.lower() for m in moods_raw if isinstance(m, str)]
            matched_moods = get_matching_moods(moods)

            disliked_moods_raw = prefs.get("disliked_moods", [])
            disliked_moods = [m.lower() for m in disliked_moods_raw if isinstance(m, str)]
            matched_disliked = get_matching_moods(disliked_moods)

            # Remove disliked moods
            matched_moods = [m for m in matched_moods if m not in matched_disliked]

            # 🔥 Fallback if nothing matched, but user wrote "select the rest"
            if not matched_moods and "select the rest" in message.content.lower():
                all_moods = list(MOODS.keys())
                matched_moods = [m for m in all_moods if m not in matched_disliked]

            if not matched_moods:
                await message.channel.send("❌ I couldn’t match any moods. Please choose from: " + ", ".join(MOODS.keys()))
                return

            user_states[f"{user_id}_moods"] = matched_moods
            user_states[f"{user_id}_disliked_moods"] = matched_disliked

        await show_final_preferences_and_fetch(message, user_id)


    elif user_states.get(user_id) == "awaiting_movie_count":
        try:
            count = int(message.content.strip())
            filtered = user_states.get(f"{user_id}_filtered_movies", [])
            if not filtered:
                await message.channel.send("⚠️ No movies found. Please try again.")
                return

            count = min(count, len(filtered))
            selected = filtered[:count]
            if count < int(message.content.strip()):
                await message.channel.send(f"⚠️ Only {count} movies matched your filters. Showing all of them:")
            await message.channel.send(f"📽️ **Here are your {count} movies:**")
            chunk = ""
            for i, movie in enumerate(selected, start=1):
                title = movie.get('title', 'Unknown Title')
                overview = movie.get('overview', 'No description available.')
                entry = f"\n{i}. **{title}**\n📖 {overview.strip()}\n"
                if len(chunk) + len(entry) > 1900:
                    await message.channel.send(chunk)
                    chunk = entry
                else:
                    chunk += entry
            if chunk.strip():
                await message.channel.send(chunk)

            # Cleanup
            for key in list(user_states.keys()):
                if str(user_id) in str(key):
                    del user_states[key]

        except ValueError:
            await message.channel.send("❌ Please enter a valid number.")

async def show_final_preferences_and_fetch(message, user_id):
    preferred = user_states.get(f"{user_id}_preferred_genres", [])
    disliked = user_states.get(f"{user_id}_disliked_genres", [])
    moods = user_states.get(f"{user_id}_moods", [])
    disliked_moods = user_states.get(f"{user_id}_disliked_moods", [])

    msg = f"**🎬 Extracted Preferences:**\n✅ **Preferred Genres:** {', '.join(preferred)}\n"
    if disliked:
        msg += f"❌ **Disliked Genres:** {', '.join(disliked)}\n"
    if moods:
        msg += f"🎭 **Mood(s):** {', '.join(m.capitalize() for m in moods)}\n"
    if disliked_moods:
        msg += f"🚫 **Disliked Moods:** {', '.join(m.capitalize() for m in disliked_moods)}\n"

    await message.channel.send(msg)

    filtered = await fetchMovies(preferred, disliked, message, user_id, moods=moods, disliked_moods=disliked_moods)
    if not filtered:
        await message.channel.send("😕 Sorry, I couldn’t find any good matches.")
        return

    user_states[f"{user_id}_filtered_movies"] = filtered
    user_states[user_id] = "awaiting_movie_count"
    await message.channel.send("🎬 How many movies do you want to see? (Enter a number)")

# Start the bot
client.run(KarenDiscord)
print("DISCORD TOKEN FROM ENV:", KarenDiscord)

