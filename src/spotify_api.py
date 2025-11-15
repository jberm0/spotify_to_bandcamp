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
    return SpotifyOAuth(
        client_id=st.secrets["SPOTIPY_CLIENT_ID"],
        client_secret=st.secrets["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=st.secrets["SPOTIPY_REDIRECT_URI"],
        scope=SCOPE,
        cache_path=None,  # VERY IMPORTANT (no shared cache)
        open_browser=False,
    )


# ------------------ AUTH LOGIC ------------------ #


def authorise():
    oauth = get_oauth()

    # --- handle callback ---
    params = st.query_params
    code = params["code"] if "code" in params else None

    if isinstance(code, list):  # Streamlit sometimes returns a list
        code = code[0]

    if code:
        st.write("Received callback from Spotify!")
        try:
            token_info = oauth.get_access_token(code, check_cache=False)

            st.session_state["token_info"] = token_info
            st.session_state["sp"] = spotipy.Spotify(auth=token_info["access_token"])

            # Clear params from URL
            st.query_params.clear()
            st.rerun()

        except Exception as e:
            st.error(f"Spotify auth error: {e}")
            st.markdown(f"[Retry login]({oauth.get_authorize_url()})")
            return

    # --- no callback? Show login link ---
    if "token_info" not in st.session_state:
        auth_url = oauth.get_authorize_url()
        st.write("Click below to log in to Spotify:")
        st.markdown(f"[Authenticate with Spotify]({auth_url})")
        return

    st.success("Authenticated!")


def get_spotify_client():
    """Ensure token is fresh, return Spotify client or None."""
    if "token_info" not in st.session_state:
        return None

    oauth = get_oauth()
    token_info = st.session_state["token_info"]

    # Refresh token if expired
    if oauth.is_token_expired(token_info):
        token_info = oauth.refresh_access_token(token_info["refresh_token"])
        st.session_state["token_info"] = token_info

    # Ensure `sp` is set for compatibility with old code
    st.session_state["sp"] = spotipy.Spotify(auth=token_info["access_token"])
    return st.session_state["sp"]


def check_authorisation(custom_message=None):
    """Require user login. Returns sp or None."""
    sp = get_spotify_client()
    if sp is None:
        msg = custom_message or "Please sign in to Spotify to continue."
        st.warning(msg)

        auth_url = get_oauth().get_authorize_url()
        st.markdown(f"[Click here to authenticate with Spotify]({auth_url})")

        return None
    return sp
