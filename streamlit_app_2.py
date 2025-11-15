import streamlit as st
import polars as pl

from saved_albums import main as albums_main
from saved_tracks import main as tracks_main
from tops import top_artists, top_tracks, top_albums
from recents import process_raw_recents
from bandcamp import compute_bandcamp_urls

if "filters" not in st.session_state:
    st.session_state.filters = {
        "artist": "",
        "album": "",
        "track": "",
    }

def clear_all_filters():
    """Sets all filter session state variables to their default (empty string)
    before the main script reruns."""
    st.session_state["filter_artist"] = ""
    st.session_state["filter_album"] = ""
    st.session_state["filter_track"] = ""
    st.session_state.filters = {"artist": "", "album": "", "track": ""}


if "filters" not in st.session_state:
    st.session_state.filters = {"artist": "", "album": "", "track": ""}
if "filter_artist" not in st.session_state:
    st.session_state["filter_artist"] = ""
if "filter_album" not in st.session_state:
    st.session_state["filter_album"] = ""
if "filter_track" not in st.session_state:
    st.session_state["filter_track"] = ""

with st.sidebar:
    st.header("🔍 Filters")

    artist_input = st.text_input(
        "Artist contains",
        key="filter_artist",
    ).strip()

    album_input = st.text_input(
        "Album contains",
        key="filter_album",
    ).strip()

    track_input = st.text_input(
        "Track contains",
        key="filter_track",
    ).strip()

    with st.expander("Current filters", False):
        st.write("Current Filters Applied:", st.session_state.filters)

    st.button("Clear Filters", on_click=clear_all_filters)

st.session_state.filters["artist"] = artist_input
st.session_state.filters["album"] = album_input
st.session_state.filters["track"] = track_input


def apply_filters(df: pl.DataFrame):

    f = st.session_state.filters

    if f["artist"]:
        df = df.filter(
            pl.col("artist_name")
            .cast(pl.List(pl.String))
            .list.join(", ")
            .str.to_lowercase()
            .str.contains(f["artist"].lower())
        )

    if f["album"] and "album_name" in df.columns:
        df = df.filter(
            pl.col("album_name").str.to_lowercase().str.contains(f["album"].lower())
        )

    if f["track"] and "track_name" in df.columns:
        df = df.filter(
            pl.col("track_name").str.to_lowercase().str.contains(f["track"].lower())
        )

    return df

top_lists, recents, albums, tracks = st.tabs(
    ["top_lists", "recents", "albums", "tracks"]
)

with top_lists:

    st.title("Top Lists")

    category = st.pills(
        "Category",
        options=["tracks", "albums", "artists"],
        selection_mode="single",
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
            df = top_albums(term)
        case _:
            df = None

    st.write(apply_filters(df))

    if st.button("Search Bandcamp"):
        if apply_filters(df) is not None and not apply_filters(df).is_empty():
            # Compute Bandcamp URLs
            df_with_urls = compute_bandcamp_urls(apply_filters(df))
            st.success("Bandcamp URLs fetched!")
            st.dataframe(
                df_with_urls,
                column_config={
                    "bandcamp_url": st.column_config.LinkColumn(
                        help="Note the bandcamp link may not always be accurate",
                    )
                },
            )
        else:
            st.warning("No data to search.")

with recents:

    st.title("Recent Plays")
    df = process_raw_recents()
    st.write(apply_filters(df))

# with albums:

#     st.title("Albums")
#     df = albums_main()

#     st.write(f"{df.height} albums pre-filter")
#     df = apply_filters(df)
#     st.write(df)

# with tracks:

#     st.title("Tracks")
#     df = tracks_main()

#     st.write(f"{df.height} tracks pre-filter")
#     df = apply_filters(df)
#     st.write(df)
