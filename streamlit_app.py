import streamlit as st
from src.tops import top_artists, top_tracks, top_albums
from src.recents import process_raw_recents
from src.bandcamp import compute_bandcamp_urls
from src.spotify_api import authorise, check_authorisation
from src.filters import clear_all_filters, apply_filters

if "sp" not in st.session_state:
    st.session_state["sp"] = None
if "code" not in st.session_state:
    st.session_state["code"] = None

if "filters" not in st.session_state:
    st.session_state.filters = {
        "artist": "",
        "album": "",
        "track": "",
    }
if "filter_artist" not in st.session_state:
    st.session_state["filter_artist"] = ""
if "filter_album" not in st.session_state:
    st.session_state["filter_album"] = ""
if "filter_track" not in st.session_state:
    st.session_state["filter_track"] = ""

with st.sidebar:
    st.header("Filters")

    artist_input = st.text_input("Artist contains", key="filter_artist").strip()
    album_input = st.text_input("Album contains", key="filter_album").strip()
    track_input = st.text_input("Track contains", key="filter_track").strip()

    with st.expander("Current filters", False):
        st.write("Current Filters Applied:", st.session_state.filters)

    st.button("Clear Filters", on_click=clear_all_filters)

st.session_state.filters["artist"] = artist_input
st.session_state.filters["album"] = album_input
st.session_state.filters["track"] = track_input

about, top_lists, recents = st.tabs(["About", "Top Lists", "Recent Tracks"])

with about:
    st.title("Spotify to Bandcamp")
    st.markdown("**intro text**")
    if check_authorisation(
        "Please log in to Spotify to view your account information."
    ):
        sp = st.session_state["sp"]
        user_info = sp.current_user()
        st.write(f"Hey, {user_info['display_name']}")
    else:
        authorise()

with top_lists:
    st.title("Top Tracks, Albums and Artists")

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

with recents:
    st.title("Last 50 Tracks Played")

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
