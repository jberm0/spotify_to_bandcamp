import streamlit as st
from src.tops import top_artists, top_tracks, top_albums
from src.recents import process_raw_recents
from src.bandcamp import return_bandcamp_dfs
from src.spotify_api import check_authorisation, force_spotify_auth
from src.filters import apply_filters, filters_setup
from src.about import about_app

st.set_page_config(initial_sidebar_state="collapsed")

if "sp" not in st.session_state:
    st.session_state["sp"] = None
if "code" not in st.session_state:
    st.session_state["code"] = None
if "spotify_token" not in st.session_state:
    st.session_state["spotify_token"] = None
if "auth_attempted" not in st.session_state:
    st.session_state["auth_attempted"] = None
if "auth_url" not in st.session_state:
    st.session_state["auth_url"] = None

filters_setup()

about, login, top_lists, recents = st.tabs(
    ["About", "Login", "Top Lists", "Recent Tracks"]
)

with about:
    st.title("Spotify to Bandcamp")
    about_app()

with login:
    force_spotify_auth()

with top_lists:
    st.title("Top Tracks, Albums and Artists")

    user_info = st.session_state["sp"].current_user()
    st.write(f"Hey, {user_info['display_name']} - please select a category and time frame and then hit search")

    if check_authorisation("Please log in to Spotify to view top lists"):
        category = st.pills(
            "Category", options=["tracks", "albums", "artists"], selection_mode="single"
        )
        term = st.pills(
            label="Term",
            options=["short_term", "medium_term", "long_term"],
            selection_mode="single",
            help="Short term is roughly 4 weeks, medium term roughly 6 months and long term roughly 1 year"
        )
        if not term:
            st.warning("If no time frame is selected, the results will be medium term")

        match category:
            case "artists":
                df = top_artists(term)
            case "tracks":
                df = top_tracks(term)
            case "albums":
                st.badge(
                    "Note that top albums are aggregated from top tracks", color="grey"
                )
                df = top_albums(term)
            case _:
                df = None

        filtered_df = apply_filters(df)

        if st.button(
            "🚨 Generate Bandcamp links 🚨",
            key="search_bandcamp_tops",
            help=f"_Click here to search bandcamp for the {category if category is not None else 'category'} listed_",
        ):
            if filtered_df is not None and not filtered_df.is_empty():
                return_bandcamp_dfs(filtered_df)
            else:
                st.warning("No data to search.")
        else:
            st.write(filtered_df)
    else:
        force_spotify_auth()

with recents:
    st.title("Last 50 Tracks Played")

    user_info = st.session_state["sp"].current_user()
    st.badge(
        f"Hey, {user_info['display_name']} - these are your last 50 played tracks"
    )

    if check_authorisation("Please log in to Spotify to view your recent tracks."):
        df = process_raw_recents()
        filtered_df = apply_filters(df)

        if st.button(
            "🚨 Generate Bandcamp links 🚨",
            key="search_bandcamp_recents",
            help="_Click here to search bandcamp for the tracks listed_",
        ):
            if filtered_df is not None and not filtered_df.is_empty():
                return_bandcamp_dfs(filtered_df)
            else:
                st.warning("No data to search.")
        else:
            st.write(filtered_df)
    else:
        force_spotify_auth()
