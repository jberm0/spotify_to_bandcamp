from spotify_api import sp
import polars as pl
import streamlit as st


def get_top_tracks(sp, time_range: str):
    limit = 100
    next = 0
    data = []
    while next < limit:
        res = sp.current_user_top_tracks(limit=50, offset=next, time_range=time_range)
        data.extend(res.get("items"))
        print(f"gathered {next} to {next + 50}")
        next = res.get("offset") + 50
    return data


def get_top_artists(sp, time_range: str):
    limit = 100
    next = 0
    data = []
    while next < limit:
        res = sp.current_user_top_artists(limit=50, offset=next, time_range=time_range)
        data.extend(res.get("items"))
        print(f"gathered {next} to {next + 50}")
        next = res.get("offset") + 50
    return data

def process_df(df):
    return (
        df.select(
            pl.col("name").alias("track_name"),
            "album",
            pl.col("artists").alias("track_artists"),
        )
        .unnest("album")
        .select(
            "track_name",
            pl.col("name").alias("album_name"),
            "track_artists",
        )
        .explode("track_artists")
        .unnest("track_artists")
        .select(
            "track_name",
            "album_name",
            pl.col("name").alias("artist_name"),
        )
        .group_by("track_name", "album_name", maintain_order=True)
        .agg("artist_name")
    )


@st.cache_data()
def top_tracks(term):
    tracks = get_top_tracks(sp, term)
    df = pl.DataFrame(tracks).select("album", "artists", "name")
    return process_df(df)


@st.cache_data()
def top_artists(term):
    artists = get_top_artists(sp, term)
    return (
        pl.DataFrame(artists)
        .select(pl.col("name").alias("artist_name"))
    )

@st.cache_data()
def top_albums(term):
    top_tracks_df = top_tracks(term)
    return (
        top_tracks_df.group_by("album_name", "artist_name")
        .agg(
            pl.count("track_name").alias("track_count"),
        )
        .filter(pl.col("track_count") > 3)
    )
