from spotify_api import sp
import pprint
import polars as pl
import os


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


def process_raw_albums():
    print("processing raw")
    df = pl.read_parquet("data/raw/saved_albums.parquet")
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
            "album_id",
            "added_at",
            "album_type",
            "album_name",
            "release_date",
            "label",
            maintain_order=True,
        )
        .agg("artist_name", "artist_id")
    )
    return df


def main():
    if os.path.exists("data/raw/saved_albums.parquet"):
        offset = pl.read_parquet("data/raw/saved_albums.parquet").height
        print(f"offset: {offset}")
        data = get_saved_albums_raw(sp, offset)
        if data:
            new_df = pl.DataFrame(data).unnest("album")
            current_df = pl.read_parquet("data/raw/saved_albums.parquet")
            (pl.concat([current_df, new_df], how="diagonal_relaxed")).write_parquet(
                "data/raw/saved_albums.parquet"
            )
        else:
            print("no new data to ingest")
    else:
        offset = 0
        data = get_saved_albums_raw(sp, offset)
        df = pl.DataFrame(data).unnest("album")
        df.write_parquet("data/raw/saved_albums.parquet")

    clean_df = process_raw_albums()
    clean_df.write_parquet("data/cleaned/saved_albums.parquet")
    print("cleaned saved albums")


if __name__ == "__main__":
    main()
