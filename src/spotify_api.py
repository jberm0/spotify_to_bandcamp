import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Load environment variables (you can also use streamlit secrets if deployed)
from dotenv import load_dotenv

load_dotenv()

# Spotify API credentials (you can store them in .env or Streamlit Secrets)
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# Spotify OAuth Scope
SCOPE = "playlist-read-private playlist-read-collaborative user-library-read user-top-read user-read-recently-played"

# Initialize the OAuth object
sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE,
)

def authorise():
    if st.session_state["sp"] is None:
        if "code" in st.query_params:
            # The user has authorized the app
            code = st.query_params["code"][0]
            st.session_state["code"] = code
            token_info = sp_oauth.get_access_token(code)
            sp = spotipy.Spotify(
                auth=token_info["access_token"]
            )
            st.session_state["sp"] = sp
            st.success("Successfully signed in to Spotify")
        else:
            # Display the authorization URL to the user
            auth_url = sp_oauth.get_authorize_url()
            st.markdown(f"[Click here to authenticate with your Spotify account]({auth_url})")
    else:
        st.success("You are already signed in!")


def check_authorisation(custom_message=None):
    if st.session_state["sp"] is None:
        auth_url = st.session_state.get("auth_url")
        if custom_message:
            st.warning(custom_message)
        else:
            st.warning("Please sign in to Spotify to see this")
        if auth_url:
            st.markdown(f"[Click here to authenticate with your Spotify account]({auth_url})")
        return False
    return True
