import polars as pl
import urllib.parse
import streamlit as st


def find_bandcamp_url_optimized(artist="", album="", track=""):
    # Handle lists from Polars rows
    if isinstance(artist, list):
        artist = artist[0]
    if isinstance(album, list):
        album = album[0]
    if isinstance(track, list):
        track = track[0]

    # Build search query
    query = " ".join([str(artist), str(album), str(track)]).strip()
    encoded = urllib.parse.quote(query)

    # Bandcamp public search URL (100% cloud-safe)
    return f"https://bandcamp.com/search?q={encoded}"


def compute_bandcamp_urls(df: pl.DataFrame) -> pl.DataFrame:
    """
    Create a separate DataFrame with bandcamp_url for each row.
    """
    artists = df["artist_name"].to_list()
    albums = (
        df["album_name"].to_list()
        if "album_name" in df.columns
        else [""] * len(artists)
    )
    tracks = (
        df["track_name"].to_list()
        if "track_name" in df.columns
        else [""] * len(artists)
    )

    # Compute URLs
    urls = [
        find_bandcamp_url_optimized(a, b, t) for a, b, t in zip(artists, albums, tracks)
    ]

    # Build DataFrame dynamically
    data = {"artist_name": artists}
    if "album_name" in df.columns:
        data["album_name"] = albums
    if "track_name" in df.columns:
        data["track_name"] = tracks
    data["bandcamp_url"] = urls

    join_cols = ["artist_name"]
    if "album_name" in df.columns:
        join_cols.append("album_name")
    if "track_name" in df.columns:
        join_cols.append("track_name")

    return df.join(pl.DataFrame(data), on=join_cols, how="left")

def return_bandcamp_dfs(df):
    df_with_urls = compute_bandcamp_urls(df)
    st.success("Bandcamp URLs generated!")
    st.dataframe(
        df_with_urls,
        column_config={
            "bandcamp_url": st.column_config.LinkColumn(
                help="The bandcamp link may not always be accurate"
            )
        },
    )