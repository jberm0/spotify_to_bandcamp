import streamlit as st
import polars as pl

def clear_all_filters():
    st.session_state["filter_artist"] = ""
    st.session_state["filter_album"] = ""
    st.session_state["filter_track"] = ""
    st.session_state.filters = {"artist": "", "album": "", "track": ""}

def apply_filters(df: pl.DataFrame):
    if df is None or df.is_empty():
        st.warning("No data yet - try selecting options above")
        return df
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

def filters_setup():
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
