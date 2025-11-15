import streamlit as st
import polars as pl

def clear_all_filters():
    st.session_state["filter_artist"] = ""
    st.session_state["filter_album"] = ""
    st.session_state["filter_track"] = ""
    st.session_state.filters = {"artist": "", "album": "", "track": ""}

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