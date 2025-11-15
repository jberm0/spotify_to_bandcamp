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
#     # Check if the 'sp' key is in session state (this means the user has already authenticated)
#     if "sp" not in st.session_state or st.session_state["sp"] is None:
#         # Check if we have a code in the query params
#         code = st.query_params.get("code")

#         if code:
#             try:
#                 # Exchange the code for an access token
#                 token_info = sp_oauth.get_access_token(
#                     code
#                 )
#                 access_token = token_info["access_token"]
#                 st.session_state["sp"] = spotipy.Spotify(
#                     auth=access_token
#                 )  # Initialize Spotify client
#                 st.success("Successfully authorized!")

#                 # Use the access token to get user info or top tracks, etc.
#                 sp = st.session_state["sp"]
#                 user_info = sp.current_user()
#                 st.write(f"Hello, {user_info['display_name']}!")

#             except Exception as e:
#                 st.error(f"Error during authorization: {str(e)}")
#                 st.markdown("[Click here to reauthorize with Spotify](%s)" % sp_oauth.get_authorize_url())
#         else:
#             # No code, so show the authorization URL
#             auth_url = sp_oauth.get_authorize_url()
#             st.markdown(f"[Click here to authorize with Spotify]({auth_url})")
#     else:
#         st.success("Already authorized with Spotify!")


# def check_authorisation(custom_message=None):
#     if st.session_state["sp"] is None:
#         auth_url = st.session_state.get("auth_url")
#         if custom_message:
#             st.warning(custom_message)
#         else:
#             st.warning("Please sign in to Spotify to see this")
#         if auth_url:
#             st.markdown(f"[Click here to authenticate with your Spotify account]({auth_url})")
#         return False
#     return True


# def clear_session_on_new_visit():
#     """Forcefully clear session data on new visits to ensure re-authentication."""
#     if "sp" in st.session_state:
#         del st.session_state["sp"]
#         st.session_state["sp"] = None  # Make sure 'sp' key is reset


# def authorise():
#     clear_session_on_new_visit()
#     # Each user has their own session, check if "sp" is in the session state for that user
#     if "sp" not in st.session_state or st.session_state["sp"] is None:
#         # Check if we have a code in the query params
#         code = st.query_params.get("code")

#         if code:
#             try:
#                 # Exchange the code for an access token
#                 token_info = sp_oauth.get_access_token(code)
#                 access_token = token_info["access_token"]
#                 st.session_state["sp"] = spotipy.Spotify(
#                     auth=access_token
#                 )  # Initialize Spotify client
#                 st.success("Successfully authorized!")

#                 # Use the access token to get user info
#                 sp = st.session_state["sp"]
#                 user_info = sp.current_user()
#                 st.write(f"Hello, {user_info['display_name']}!")

#             except Exception as e:
#                 st.error(f"Error during authorization: {str(e)}")
#                 # Provide a reauthorization link in case of failure
#                 st.markdown(
#                     "[Click here to reauthorize with Spotify](%s)"
#                     % sp_oauth.get_authorize_url()
#                 )

#         else:
#             # No code, so show the authorization URL
#             auth_url = sp_oauth.get_authorize_url()
#             # Store the auth URL in session state for potential future access
#             st.session_state["auth_url"] = auth_url
#             st.markdown(
#                 f"[Click here to authorize with your Spotify account]({auth_url})"
#             )
#     else:
#         st.success("Already authorized with Spotify!")


# def check_authorisation(custom_message=None):
#     # Check if the user is authorized (i.e., 'sp' key exists in session_state)
#     if st.session_state.get("sp") is None:
#         auth_url = st.session_state.get("auth_url")
#         if custom_message:
#             st.warning(custom_message)
#         else:
#             st.warning("Please sign in to Spotify to see this content.")
#         if auth_url:
#             st.markdown(
#                 f"[Click here to authenticate with your Spotify account]({auth_url})"
#             )
#         return False
#     return True

# import streamlit as st
# import spotipy
# from spotipy.oauth2 import SpotifyOAuth

# # Spotify OAuth Scope
# SCOPE = (
#     "playlist-read-private playlist-read-collaborative "
#     "user-library-read user-top-read user-read-recently-played"
# )

# --- Helpers ---


def get_oauth():
    """Create a new OAuth manager (no shared cache!)."""
    return SpotifyOAuth(
        client_id=st.secrets["SPOTIPY_CLIENT_ID"],
        client_secret=st.secrets["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=st.secrets["SPOTIPY_REDIRECT_URI"],
        scope=SCOPE,
        cache_path=None,  # <- IMPORTANT so Spotify tokens are NOT stored on disk
        open_browser=False,  # prevent Streamlit from trying to open browser
    )


def get_spotify_client():
    """Return authenticated Spotify client or None."""
    if "token_info" not in st.session_state:
        return None

    oauth = get_oauth()
    token_info = st.session_state["token_info"]

    # Refresh the token if expired
    if oauth.is_token_expired(token_info):
        token_info = oauth.refresh_access_token(token_info["refresh_token"])
        st.session_state["token_info"] = token_info

    return spotipy.Spotify(auth=token_info["access_token"])


# --- Authentication Flow ---


def authorise():
    """Start authentication or finish callback."""
    oauth = get_oauth()
    code = st.query_params.get("code")

    # If Spotify redirected back with a code
    if code:
        try:
            token_info = oauth.get_access_token(
                code, check_cache=False  # ensure no shared cache
            )
            st.session_state["token_info"] = token_info

            # Cleanup URL and re-run
            st.query_params.clear()
            st.rerun()

        except Exception as e:
            st.error(f"Error during Spotify authentication: {e}")
            st.markdown(f"[Retry login]({oauth.get_authorize_url()})")
            return

    # If no token yet, show login link
    if "token_info" not in st.session_state:
        auth_url = oauth.get_authorize_url()
        st.markdown(f"[Click here to log in with Spotify]({auth_url})")
        return

    # Already authenticated
    st.success("Authenticated with Spotify!")


def check_authorisation(custom_message=None):
    """Require authentication before showing protected content."""
    sp = get_spotify_client()
    if sp is None:
        msg = custom_message or "Please sign in to Spotify to continue."
        st.warning(msg)

        oauth = get_oauth()
        auth_url = oauth.get_authorize_url()
        st.markdown(f"[Click here to authenticate with Spotify]({auth_url})")

        return None

    return sp


# --- Example protected section ---
# Call this at the top of any page requiring login:
# sp = check_authorisation()
# if not sp:
#     st.stop()
# user = sp.current_user()
# st.write(f"Welcome {user['display_name']}!")
