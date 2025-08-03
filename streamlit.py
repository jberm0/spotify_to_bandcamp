import streamlit as st
import polars as pl
import os


albums, tracks, top_lists = st.tabs(["albums", "tracks", "top_lists"])

with st.sidebar:
    st.header("🔍 Filters")
    show_purchased = st.checkbox("Show Purchased Only", False)
    show_unpurchased = st.checkbox("Show Unpurchased Only", False)
    artist_filter = st.text_input("Search by Artist", "").strip()
    album_filter = st.text_input("Search by Album", "").strip()

def load_data(tab):
    if tab == "albums" and albums:
        if os.path.exists(
            "data/streamlit/albums.parquet"
        ):
            return pl.read_parquet("data/streamlit/albums.parquet").select(
                "album_id",
                "album_name",
                "artist_name",
                "label",
                "release_date",
                "purchased",
            )
        else:
            return pl.read_parquet("data/cleaned/saved_albums.parquet").select(
                "album_id", "album_name", "artist_name", "label", "release_date", pl.lit(False).alias("purchased")
            )
    elif tab == "tracks" and tracks:
        if os.path.exists("data/streamlit/tracks.parquet"):
            return pl.read_parquet("data/streamlit/tracks.parquet").select(
                "track_id",
                "track_name",
                "album_name",
                "artist_name",
                "release_date",
                "purchased",
            )
        else:
            return pl.read_parquet("data/cleaned/saved_tracks.parquet").select(
                "track_id",
                "track_name",
                "album_name",
                "artist_name",
                "release_date",
                pl.lit(False).alias("purchased"),
            )
    elif tab == "top_lists" and top_lists:
        category = st.pills("Category", options=["artists", "tracks"], selection_mode="single")
        term = st.pills(
            "Term",
            options=["short_term", "medium_term", "long_term"],
            selection_mode="single",
        )

        if category == "artists":
            columns = ["name"]
            dir = "raw"
        else:
            columns = ["track_name", "artist_name", "album_name"]
            dir = "cleaned"

        if category and term:
            return pl.read_parquet(f"data/{dir}/top_{category}_{term}.parquet").select(columns)


with albums:

    def update_purchased_album(df, album_id, purchased):
        df = df.with_columns(
            pl.when(pl.col("album_id") == album_id)
            .then(purchased)
            .otherwise(pl.col("purchased"))
            .alias("purchased")
        )
        return df

    def main_albums():
        st.title("Albums")

        if "df_albums" not in st.session_state:
            st.session_state.df_albums = load_data("albums")

        df_albums = st.session_state.df_albums

        if "album_id" not in df_albums.columns:
            st.error("Your Spotify data must include a 'album_id' column.")
            return

        if "purchased" not in df_albums.columns:
            df_albums = df_albums.with_columns(pl.lit(False).alias("purchased"))

        filtered_df = df_albums.clone()

        if show_purchased and not show_unpurchased:
            filtered_df = filtered_df.filter(pl.col("purchased") == True)
        elif show_unpurchased and not show_purchased:
            filtered_df = filtered_df.filter(pl.col("purchased") == False)

        st.write(f"{filtered_df.height} albums")

        st.write(filtered_df)

        if artist_filter:
            filtered_df = filtered_df.filter(pl.col("artist_name").cast(pl.List(pl.String)).list.join(", ").str.contains(artist_filter))
        if album_filter:
            filtered_df = filtered_df.filter(pl.col("album_name").str.contains(album_filter))

        if artist_filter or album_filter:
            selected_album = filtered_df.select("album_id", "album_name", "artist_name", "purchased")

            st.write(selected_album)

            if selected_album.height > 1:
                st.write("please filter down to a single album to mark as purchased")
            elif selected_album.height == 0:
                st.write("no albums found matching those filters")
            else:
                is_purchased = selected_album.item(0, "purchased")
                album_id = selected_album.item(0, "album_id")

                st.write(is_purchased)
                st.write(album_id)

                # Show purchase/unpurchase button based on current purchase status
                if is_purchased:
                    if st.button("❌ Unmark as purchased", key="unpurchase_album"):
                        df_albums = update_purchased_album(df_albums, album_id, False)
                        st.session_state.df_spotify = df_albums
                        st.success("Album unmarked as purchased.")
                else:
                    if st.button("✅ Mark as purchased (including partial)", key="purchase_album"):
                        df_albums = update_purchased_album(df_albums, album_id, True)
                        st.session_state.df_albums = df_albums
                        st.success("Album marked as purchased.")
                        st.write(df_albums.filter(pl.col("album_id") == album_id))

                albums_button = st.button("Save Changes", key="save_changes_albums")
                if albums_button:
                    st.session_state.df_albums.write_parquet(
                        "data/streamlit/albums.parquet"
                    )
                    st.success("Changes saved!")
                    st.write(df_albums.filter(pl.col("purchased") == True))

    if __name__ == "__main__":
        main_albums()


with tracks:

    def update_purchased_track(df, track_id, purchased):
        df = df.with_columns(
            pl.when(pl.col("track_id") == track_id)
            .then(purchased)
            .otherwise(pl.col("purchased"))
            .alias("purchased")
        )
        return df

    def main_tracks():
        st.title("Tracks")

        if "df_tracks" not in st.session_state:
            st.session_state.df_tracks = load_data("tracks")

        df_tracks = st.session_state.df_tracks

        if "track_id" not in df_tracks.columns:
            st.error("Your Spotify data must include a 'track_id' column.")
            return

        if "purchased" not in df_tracks.columns:
            df_tracks = df_tracks.with_columns(pl.lit(False).alias("purchased"))

        filtered_df = df_tracks.clone()

        if show_purchased and not show_unpurchased:
            filtered_df = filtered_df.filter(pl.col("purchased") == True)
        elif show_unpurchased and not show_purchased:
            filtered_df = filtered_df.filter(pl.col("purchased") == False)

        st.write(f"{filtered_df.height} tracks")

        st.write(filtered_df)

        track_filter = st.text_input("Search by Track", "").strip()

        if artist_filter:
            filtered_df = filtered_df.filter(
                pl.col("artist_name")
                .cast(pl.List(pl.String))
                .list.join(", ")
                .str.contains(artist_filter)
            )
        if album_filter:
            filtered_df = filtered_df.filter(
                pl.col("album_name").str.contains(album_filter)
            )
        if track_filter:
            filtered_df = filtered_df.filter(
                pl.col("track_name").str.contains(track_filter)
            )

        if artist_filter or album_filter or track_filter:
            selected_album = filtered_df.select(
                "track_id", "track_name", "album_name", "artist_name", "purchased"
            )

            st.write(selected_album)

            if selected_album.height > 1:
                st.write("please filter down to a single track to mark as purchased")
            elif selected_album.height == 0:
                st.write("no tracks found matching those filters")
            else:
                is_purchased = selected_album.item(0, "purchased")
                track_id = selected_album.item(0, "track_id")

                st.write(is_purchased)
                st.write(track_id)

                # Show purchase/unpurchase button based on current purchase status
                if is_purchased:
                    if st.button("❌ Unmark as purchased", key="unpurchase_track"):
                        df_tracks = update_purchased_track(df_tracks, track_id, False)
                        st.session_state.df_tracks = df_tracks
                        st.success("Track unmarked as purchased.")
                else:
                    if st.button("✅ Mark as purchased", key="purchase_track"):
                        df_tracks = update_purchased_track(df_tracks, track_id, True)
                        st.session_state.df_tracks = df_tracks
                        st.success("Track marked as purchased.")
                        st.write(df_tracks.filter(pl.col("track_id") == track_id))

                tracks_button = st.button("Save Changes", key="save_changes_tracks")
                if tracks_button:
                    st.session_state.df_tracks.write_parquet(
                        "data/streamlit/tracks.parquet"
                    )
                    st.success("Changes saved!")
                    st.write(df_tracks.filter(pl.col("purchased") == True))

    if __name__ == "__main__":
        main_tracks()

with top_lists:

    st.title(f"Top Lists")

    data = load_data("top_lists")

    st.write(data)
