from spotify_api import sp
import polars as pl


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
            pl.col("id").alias("track_id"),
            pl.col("name").alias("track_name"),
            "album",
            pl.col("artists").alias("track_artists"),
        )
        .unnest("album")
        .select(
            "track_id",
            "track_name",
            pl.col("name").alias("album_name"),
            "track_artists",
        )
        .explode("track_artists")
        .unnest("track_artists")
        .select(
            "track_id",
            "track_name",
            "album_name",
            pl.col("name").alias("artist_name"),
        )
        .group_by("track_id", "track_name", "album_name", maintain_order=True)
        .agg("artist_name")
    )

def top_tracks(term):
    tracks = get_top_tracks(sp, term)
    df = pl.DataFrame(tracks).select("album", "artists", "id", "name")
    return process_df(df)

def top_artists(term):
    artists = get_top_artists(sp, term)
    return pl.DataFrame(artists).select("id", "name")


# def main():
#     for term in ["short_term", "medium_term", "long_term"]:
#         tracks = get_top_tracks(sp, term)
#         tracks_df = pl.DataFrame(tracks).select("album", "artists", "id", "name")
#         tracks_df.write_parquet(f"data/raw/top_tracks_{term}.parquet")

#         tracks_cleaned = (
#             tracks_df.select(
#                 pl.col("id").alias("track_id"),
#                 pl.col("name").alias("track_name"),
#                 "album",
#                 pl.col("artists").alias("track_artists"),
#             )
#             .unnest("album")
#             .select(
#                 "track_id",
#                 "track_name",
#                 pl.col("name").alias("album_name"),
#                 "track_artists",
#             )
#             .explode("track_artists")
#             .unnest("track_artists")
#             .select(
#                 "track_id",
#                 "track_name",
#                 "album_name",
#                 pl.col("name").alias("artist_name"),
#             )
#             .group_by(
#                 "track_id",
#                 "track_name",
#                 "album_name",
#                 maintain_order=True
#             )
#             .agg("artist_name")
#         )
#         tracks_cleaned.write_parquet(f"data/cleaned/top_tracks_{term}.parquet")

#         artists = get_top_artists(sp, term)
#         artists_df = pl.DataFrame(artists).select("id", "name")
#         artists_df.write_parquet(f"data/raw/top_artists_{term}.parquet")
