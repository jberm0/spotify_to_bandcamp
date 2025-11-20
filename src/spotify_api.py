import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import uuid

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

    # Create unique session ID
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    cache_dir = "spotify_cache"

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # Build OAuth object (per user, stored in session state!)
    if "oauth" not in st.session_state:
        st.session_state.oauth = SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=SCOPE,
            cache_path=f".{cache_dir}/cache-{st.session_state.session_id}",
        )

    oauth = st.session_state.oauth

    # Already authenticated?
    if "sp" in st.session_state and st.session_state["sp"]:
        st.success("Successfully authorized!")
        user_info = st.session_state["sp"].current_user()
        st.write(f"Hey, {user_info['display_name']}")
        return True

    # Look for the 'code' from Spotify's redirect
    code = st.query_params.get("code")

    if code:
        try:
            token_info = oauth.get_access_token(code, as_dict=True)
            st.session_state["sp_token_info"] = token_info
            st.session_state["sp"] = spotipy.Spotify(auth=token_info["access_token"])

            # IMPORTANT: Clear the code from the URL -> prevents cross-user login
            st.query_params.clear()
            st.rerun()

        except Exception as e:
            st.error(f"Authorization error: {e}")
            st.session_state["sp"] = None
            st.session_state["sp_token_info"] = None

    # No token yet → show login URL
    auth_url = oauth.get_authorize_url()
    st.session_state["auth_url"] = auth_url
    st.warning("Please authorise with Spotify to continue.")
    st.markdown(f"[**Login to Spotify**]({auth_url})")
    st.stop()


def check_authorisation(custom_message=None):
    sp_client = st.session_state.get("sp")

    if sp_client is None:
        auth_url = st.session_state.get("auth_url")

        if custom_message:
            st.warning(custom_message)
        else:
            st.warning("Please sign in to Spotify to see this")

        if auth_url:
            st.markdown(
                f"[Click here to authenticate with your Spotify account]({auth_url})"
            )

        return False

    return True
