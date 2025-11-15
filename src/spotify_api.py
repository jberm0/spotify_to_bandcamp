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

# sp = Spotify(
#     auth_manager=SpotifyOAuth(
#         client_id=SPOTIPY_CLIENT_ID,
#         client_secret=SPOTIPY_CLIENT_SECRET,
#         redirect_uri=SPOTIPY_REDIRECT_URI,
#         scope="playlist-read-private playlist-read-collaborative user-library-read user-top-read user-read-recently-played",
#     )
# )

sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope,
)


query_params = st.query_params()
if "code" in query_params:
    # If we have the code, we can get the access token
    auth_code = query_params["code"][0]
    token_info = sp_oauth.get_access_token(auth_code)
    sp = spotipy.Spotify(auth=token_info["access_token"])

    st.success("Successfully authenticated with Spotify!")
    # You can now use `sp` to interact with Spotify API
else:
    # If no code is present, the user hasn't authorized the app yet
    auth_url = sp_oauth.get_authorize_url()
    st.markdown(f"[Click here to authenticate with Spotify]({auth_url})")
