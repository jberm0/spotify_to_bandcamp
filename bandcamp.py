import polars as pl
import requests
from bs4 import BeautifulSoup
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import time


import requests
from bs4 import BeautifulSoup
import urllib.parse


def find_bandcamp_url_optimized(artist="", album="", track=""):
    if isinstance(artist, list):
        artist = artist[0]
    query = f"{artist} {album} {track}"  # fallback

    encoded = urllib.parse.quote(query)
    search_url = f"https://bandcamp.com/search?q={encoded}"

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/58.0.3029.110 Safari/537.36"
            )
        }
        r = requests.get(search_url, timeout=10, headers=headers)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        for item in soup.select("li.searchresult a[href]"):
            href = item["href"]
            return href

    except Exception as e:
        print(f"Error fetching URL for {query}: {e}")
        return None

    return None


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
        find_bandcamp_url_optimized(a, b, t)
        for a, b, t in zip(artists, albums, tracks)
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
