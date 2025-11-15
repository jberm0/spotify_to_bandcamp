from spotify_api import sp
import pprint
import polars as pl
import os
import streamlit as st


def get_saved_albums_raw(sp, offset: int):
    total_albums = sp.current_user_saved_albums(market="GB", offset=0, limit=1).get(
        "total"
    )
    next = offset
    print(f"total albums: {total_albums}")
    data = []
    while next < total_albums:
        res = sp.current_user_saved_albums(market="GB", offset=next, limit=50)
        data.extend(res.get("items"))
        print(f"gathered {next} to {next + 50}")
        next = res.get("offset") + 50
    return data


def process_raw_albums(df):
    print("processing raw")
    # df = pl.read_parquet("data/raw/saved_albums.parquet")
    df = (
        df.select(
            pl.col("id").alias("album_id"),
            "added_at",
            "album_type",
            pl.col("name").alias("album_name"),
            "release_date",
            "artists",
            "label",
        )
        .explode("artists")
        .unnest("artists")
        .select(
            "album_id",
            "added_at",
            "album_type",
            "album_name",
            "release_date",
            pl.col("name").alias("artist_name"),
            pl.col("id").alias("artist_id"),
            "label",
        )
        .group_by(
            "album_name",
            "added_at",
            "album_type",
            "release_date",
            "label",
            maintain_order=True,
        )
        .agg("artist_name")
    )
    return df


@st.cache_data(ttl=3600, show_spinner=True, show_time=True)
def main():
    data = get_saved_albums_raw(sp, 0)
    df = pl.DataFrame(data).unnest("album")
    return process_raw_albums(df)
