import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Spotify API credentials
CLIENT_ID = os.getenv("CLIENT_ID") # Your spotify client id
CLIENT_SECRET_CODE = os.getenv("CLIENT_SECRET_CODE") # Your spotify client secret code

# User input for the date
date = input("What date top 100 songs are you interested in listening to? Please input the date in the format YYYY-MM-DD: \n")
url = f"https://www.billboard.com/charts/hot-100/{date}/"

# Spotify authorization
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET_CODE,
        redirect_uri="http://example.com",
        scope="playlist-modify-private",
        show_dialog=True,
        cache_path="token.txt"
    )
)

# Get the user ID
user_id = sp.current_user()["id"]

# Send a request to the Billboard Hot 100 chart URL and parse the HTML content
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Extract song titles from the HTML
top_100_songs_list = soup.find_all(name="h3", class_='a-no-trucate')
new_data = [song.get_text(strip=True) for song in top_100_songs_list]

# Search for each song on Spotify and collect their URIs
song_uris = []
year = date.split("-")[0]
for song in new_data:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist on Spotify. Skipped.")

# Create a new private playlist on Spotify
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)

# Add songs to the newly created playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

print(f"Playlist '{date} Billboard 100' created successfully!")
