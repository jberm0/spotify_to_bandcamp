import streamlit as st
import polars as pl
import os

from saved_albums import main as albums_main
from saved_tracks import main as tracks_main
from tops import top_artists, top_tracks, top_albums
from recents import process_raw_recents


(
    top_lists,
    recents,
    albums,
    tracks,
) = st.tabs(["top_lists", "recents", "albums", "tracks"])

with st.sidebar:
    st.header("🔍 Filters")
    artist_filter = st.text_input("Search by Artist", "").strip()
    album_filter = st.text_input("Search by Album", "").strip()

def load_data(tab):
    if tab == "albums" and albums:
        return pl.read_parquet("data/cleaned/saved_albums.parquet").select(
            "album_id", "album_name", "artist_name", "label", "release_date"
        )
    elif tab == "tracks" and tracks:
        return pl.read_parquet("data/cleaned/saved_tracks.parquet").select(
            "track_id",
            "track_name",
            "album_name",
            "artist_name",
            "release_date",
        )


with top_lists:

    st.title(f"Top Lists")

    category = st.pills(
        "Category",
        options=[
            "tracks",
            "albums",
            "artists"
        ],
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

    st.write(df)

with recents:

    df = process_raw_recents()
    st.write(df)

with albums:

    def main_albums():
        st.title("Albums")

        df = albums_main()

        st.write(f"{df.height} albums")

        if artist_filter:
            df = df.filter(
                pl.col("artist_name")
                .cast(pl.List(pl.String))
                .list.join(", ")
                .str.to_lowercase()
                .str
                .contains(artist_filter.lower())
            )
        if album_filter:
            df = df.filter(
                pl.col("album_name").str.to_lowercase().str.contains(album_filter)
            )

        st.write(df)

    if __name__ == "__main__":
        main_albums()


with tracks:

    def main_tracks():
        st.title("Tracks")

        df = tracks_main()

        st.write(f"{df.height} tracks")

        track_filter = st.text_input("Search by Track", "").strip()

        if artist_filter:
            df = df.filter(
                pl.col("artist_name")
                .cast(pl.List(pl.String))
                .list.join(", ")
                .str.contains(artist_filter)
            )
        if album_filter:
            df = df.filter(
                pl.col("album_name").str.contains(album_filter)
            )
        if track_filter:
            df = df.filter(
                pl.col("track_name").str.contains(track_filter)
            )

        st.write(df)

    if __name__ == "__main__":
        main_tracks()
