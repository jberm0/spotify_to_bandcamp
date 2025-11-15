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

# SPOTIPY_CLIENT_ID = st.secret("SPOTIPY_CLIENT_ID")
# SPOTIPY_CLIENT_SECRET = st.secret("SPOTIPY_CLIENT_SECRET")
# SPOTIPY_REDIRECT_URI = st.secret("SPOTIPY_REDIRECT_URI")

# http://127.0.0.1:8501/callback


# Spotify OAuth Scope
SCOPE = "playlist-read-private playlist-read-collaborative user-library-read user-top-read user-read-recently-played"

# Initialize the OAuth object
sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE,
)

# def authorise():
#     if st.session_state["sp"] is None:
#         if "code" in st.query_params:
#             # The user has authorized the app
#             code = st.query_params["code"][0]
#             st.session_state["code"] = code
#             token_info = sp_oauth.get_access_token(code)
#             sp = spotipy.Spotify(
#                 auth=token_info["access_token"]
#             )
#             st.session_state["sp"] = sp
#             st.success("Successfully signed in to Spotify")
#         else:
#             # Display the authorization URL to the user
#             auth_url = sp_oauth.get_authorize_url()
#             st.markdown(f"[Click here to authenticate with your Spotify account]({auth_url})")
#     else:
#         st.success("You are already signed in!")


def authorise():
    # Check if the 'sp' key is in session state (this means the user has already authenticated)
    if "sp" not in st.session_state or st.session_state["sp"] is None:
        # Check if we have a code in the query params
        code = st.query_params.get("code")

        if code:
            st.write(f"Received code: {code}")
            try:
                # Exchange the code for an access token
                token_info = sp_oauth.get_access_token(
                    code
                )
                access_token = token_info["access_token"]
                st.session_state["sp"] = spotipy.Spotify(
                    auth=access_token
                )  # Initialize Spotify client
                st.success("Successfully authorized!")

                # Use the access token to get user info or top tracks, etc.
                sp = st.session_state["sp"]
                user_info = sp.current_user()
                st.write(f"Hello, {user_info['display_name']}!")

            except Exception as e:
                st.error(f"Error during authorization: {str(e)}")
                st.markdown("[Click here to reauthorize with Spotify](%s)" % sp_oauth.get_authorize_url())
        else:
            # No code, so show the authorization URL
            auth_url = sp_oauth.get_authorize_url()
            st.markdown(f"[Click here to authorize with Spotify]({auth_url})")
    else:
        st.success("Already authorized with Spotify!")


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
