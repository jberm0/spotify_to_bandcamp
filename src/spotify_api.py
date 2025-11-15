import streamlit as st
import spotipy

SPOTIPY_CLIENT_ID = st.secrets["SPOTIPY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = st.secrets["SPOTIPY_CLIENT_SECRET"]
SPOTIPY_REDIRECT_URI = st.secrets["SPOTIPY_REDIRECT_URI"]

scope = "playlist-read-private playlist-read-collaborative user-library-read user-top-read user-read-recently-played"

# sp = spotipy.Spotify(
#     auth_manager=spotipy.SpotifyOAuth(
#         client_id=SPOTIPY_CLIENT_ID,
#         client_secret=SPOTIPY_CLIENT_SECRET,
#         redirect_uri=SPOTIPY_REDIRECT_URI,
#         scope=scope,
#     )
# )

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

sp = Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope="playlist-read-private playlist-read-collaborative user-library-read user-top-read user-read-recently-played",
    )
)
