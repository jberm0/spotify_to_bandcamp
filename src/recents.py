from spotify_api import sp
import pprint
import polars as pl
import os
import streamlit as st

from datetime import datetime, timedelta
import time


def one_month_ago_unix():
    now = datetime.now()
    one_month_ago = now - timedelta(days=30)
    after_timestamp = int(one_month_ago.timestamp() * 1000)

    return after_timestamp


def now_unix():
    now = datetime.now()
    return int(now.timestamp() * 1000)


def get_recent_tracks():
    ts = one_month_ago_unix()
    recents = sp.current_user_recently_played(limit=50, after=ts)
    return recents


def process_raw_recents():
    recents = get_recent_tracks()
    return (
        pl.DataFrame(recents)
        .unnest("items")
        .select("track", "played_at")
        .unnest("track")
        .select(
            pl.col("album").struct.field("name").alias("album"),
            pl.col("album").struct.field("artists"),
            pl.col("id").alias("track_id"),
            pl.col("name").alias("track_name"),
            "played_at",
        )
        .explode("artists")
        .unnest("artists")
        .select("album", "name", "track_id", "track_name", "played_at")
        .group_by("track_name", "played_at", "album")
        .agg("name")
        .select(
            "track_name",
            pl.col("album").alias("album_name"),
            pl.col("name").alias("artist_name"),
            pl.max("played_at")
            .over("track_name", "album", "name")
            .alias("last_played"),
            pl.count("played_at")
            .over("track_name", "album", "name")
            .alias("recent_track_plays"),
            pl.count("played_at")
            .over("album", "name")
            .alias("recent_songs_played_from_album"),
        )
        .unique()
    )
