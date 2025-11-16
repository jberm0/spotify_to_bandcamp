import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

def running_locally():
    try:
        host = st.get_option("browser.serverAddress")
        return host.startswith("localhost")
    except:
        return False


if running_locally():
    SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
    SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
    SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
else:
    SPOTIPY_REDIRECT_URI = st.secrets["SPOTIPY_REDIRECT_URI"]
    SPOTIPY_CLIENT_ID = st.secrets["SPOTIPY_CLIENT_ID"]
    SPOTIPY_CLIENT_SECRET = st.secrets["SPOTIPY_CLIENT_SECRET"]

# http://127.0.0.1:8501/callback


# Spotify OAuth Scope
SCOPE = "playlist-read-private playlist-read-collaborative user-library-read user-top-read user-read-recently-played"


def force_spotify_auth():
    """
    Forces a user to authenticate with Spotify at the start of a new session.
    Stops script execution until successful login and redirect.
    """

    sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
        cache_path=None
    )

    # 1. Check if we already have an active Spotify client instance in session state
    if st.session_state["sp"] is not None:
        st.success("Successfully authorized!")
        return True  # User is authenticated, proceed with the app

    # 2. Check for a 'code' in the URL query params (Spotify redirected back here)
    code = st.query_params.get("code")

    if code:
        try:
            # Exchange the code for an access token and refresh token
            token_info = sp_oauth.get_access_token(code)

            # Store token info in session state
            st.session_state["sp_token_info"] = token_info

            # Initialize the Spotify client with the access token
            st.session_state["sp"] = spotipy.Spotify(auth=token_info["access_token"])
            st.success("Successfully authorized!")

            # Rerun the script to clear the 'code' from the URL and re-render the clean UI
            st.rerun()
            return True  # This line won't be reached because rerun happens, but it's good practice

        except Exception as e:
            st.error(f"Error during authorization: {str(e)}")
            st.session_state["sp_token_info"] = None
            st.session_state["sp"] = None

    # 3. If no token and no code, the user needs to log in
    else:
        auth_url = sp_oauth.get_authorize_url()
        st.warning("Please authorize with Spotify to use this application.")
        st.markdown(f"[**Login to Spotify**]({auth_url})")

        # CRITICAL: Stop the script execution here
        # Prevents the rest of your app from running until the user logs in and reruns
        st.stop()

    return False  # Should be unreachable due to st.stop()


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
