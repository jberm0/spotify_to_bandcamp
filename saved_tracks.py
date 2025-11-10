from spotify_api import sp
import pprint
import polars as pl
import os
import streamlit as st


def get_saved_tracks_raw(sp, offset: int):
    total_tracks = sp.current_user_saved_tracks(market="GB", offset=0, limit=1).get(
        "total"
    )
    next = offset
    print(f"total tracks: {total_tracks}")
    data = []
    while next < total_tracks:
        res = sp.current_user_saved_tracks(market="GB", offset=next, limit=50)
        data.extend(res.get("items"))
        print(f"gathered {next} to {next + 50}")
        next = res.get("offset") + 50
    return data


def process_raw_tracks(df):
    print("processing raw")
    # df = pl.read_parquet("data/raw/saved_tracks.parquet")
    df = (
        df.select(
            "added_at",
            "album",
            pl.col("artists").alias("track_artists"),
            pl.col("id").alias("track_id"),
            pl.col("name").alias("track_name"),
        )
        .unnest("album")
        .select(
            "added_at",
            "track_artists",
            "track_id",
            "track_name",
            "artists",
            pl.col("id").alias("album_id"),
            pl.col("name").alias("album_name"),
            "release_date",
        )
        .explode("artists")
        .unnest("artists")
        .select(
            "added_at",
            "track_id",
            "track_name",
            "album_id",
            "album_name",
            "release_date",
            pl.col("id").alias("artist_id"),
            pl.col("name").alias("artist_name"),
        )
        .group_by(
            "added_at",
            "track_id",
            "track_name",
            "album_name",
            "release_date",
            maintain_order=True,
        )
        .agg("artist_name", "artist_id")
    )
    return df


# def main():
#     if os.path.exists("data/raw/saved_tracks.parquet"):
#         offset = pl.read_parquet("data/raw/saved_tracks.parquet").height
#         print(f"offset: {offset}")
#         data = get_saved_tracks_raw(sp, offset)
#         if data:
#             new_df = pl.DataFrame(data).unnest("track")
#             current_df = pl.read_parquet("data/raw/saved_tracks.parquet")
#             (pl.concat([current_df, new_df], how="diagonal_relaxed")).write_parquet(
#                 "data/raw/saved_tracks.parquet"
#             )
#         else:
#             print("no new data to ingest")
#     else:
#         offset = 0
#         data = get_saved_tracks_raw(sp, offset)
#         df = pl.DataFrame(data).unnest("track")
#         df.write_parquet("data/raw/saved_tracks.parquet")

#     clean_df = process_raw_tracks()
#     clean_df.write_parquet("data/cleaned/saved_tracks.parquet")
#     print("cleaned saved tracks")

@st.cache_data()
def main():
    data = get_saved_tracks_raw(sp, 0)
    df = pl.DataFrame(data).unnest("track")
    return process_raw_tracks(df)
