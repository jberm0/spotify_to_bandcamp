import streamlit as st
from src.tops import top_artists, top_tracks, top_albums
from src.recents import process_raw_recents
from src.bandcamp import compute_bandcamp_urls
from src.spotify_api import check_authorisation, force_spotify_auth
from src.filters import clear_all_filters, apply_filters, filters_setup
from src.about import about_app

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

login, about, top_lists, recents = st.tabs(
    ["Login", "About", "Top Lists", "Recent Tracks"]
)

with about:
    st.title("Spotify to Bandcamp")
    about_app()

with login:
    force_spotify_auth()

with top_lists:
    st.title("Top Tracks, Albums and Artists")

    st.badge(f"{st.session_state['sp'].current_user()}")

    if check_authorisation("Please log in to Spotify to view top lists."):
        category = st.pills(
            "Category", options=["tracks", "albums", "artists"], selection_mode="single"
        )
        term = st.pills(
            "Term",
            options=["short_term", "medium_term", "long_term"],
            selection_mode="single",
        )

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

        if st.button("Search Bandcamp", key="search_bandcamp_tops"):
            if filtered_df is not None and not filtered_df.is_empty():
                df_with_urls = compute_bandcamp_urls(filtered_df)
                st.success("Bandcamp URLs fetched!")
                st.dataframe(
                    df_with_urls,
                    column_config={
                        "bandcamp_url": st.column_config.LinkColumn(
                            help="Please note the bandcamp link may not always be accurate"
                        )
                    },
                )
            else:
                st.warning("No data to search.")
        else:
            st.write(filtered_df)
    else:
        force_spotify_auth()

with recents:
    st.title("Last 50 Tracks Played")

    st.badge(f"{st.session_state['sp'].current_user()}")

    if check_authorisation("Please log in to Spotify to view your recent tracks."):
        df = process_raw_recents()
        filtered_df = apply_filters(df)

        if st.button("Search Bandcamp", key="search_bandcamp_recents"):
            if filtered_df is not None and not filtered_df.is_empty():
                df_with_urls = compute_bandcamp_urls(filtered_df)
                st.success("Bandcamp URLs fetched!")
                st.dataframe(
                    df_with_urls,
                    column_config={
                        "bandcamp_url": st.column_config.LinkColumn(
                            help="Please note the bandcamp link may not always be accurate"
                        )
                    },
                )
            else:
                st.warning("No data to search.")
        else:
            st.write(filtered_df)
    else:
        force_spotify_auth()
