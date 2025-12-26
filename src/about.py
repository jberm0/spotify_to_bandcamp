import streamlit as st

def about_app():
    st.markdown(
        """
    Hey :)
    
    This is a simple application that allows you to review your Spotify listening activity and search Bandcamp, where you can buy music directly from artists.

    It was inspired partly by [MerchTable](https://hypem.com/merch-table) and my own desire to move away from using Spotify so heavily.

    Buying music can be expensive, so the idea is simple: here you can see what you are listening to the most, and buy it directly.
            
    ### How to use:
    1. **Log in with Spotify:** You'll need to grant permission to access your Spotify listening data. You can do this on the 'Login' tab above. 
    If you can't log in, it will probably be because your Spotify account isn't linked, message me and I can help with this. 
    If you can login, be aware a new tab will open and you will be able to continue using the application.
    2. **See your top music:** View your top tracks, albums, and artists over short, medium, or long-term periods. You can use filters on the left sidebar to search if you like.
    3. **Generate Bandcamp links:** Create search links for your favorite tracks, albums, and artists. Click the link to go to Bandcamp.
    4. **Support artists:** Consider purchasing music from the Bandcamp links to directly support the artists.

    ### Important limitations:
    1. **Spotify API limits:** Only 25 users can access this app via Spotify's API.
    2. **Bandcamp search links:** Bandcamp does not allow web scraping. The URLs generated are search result links, not direct links to a track or album page. Not all music will be on Bandcamp, so search results won't be perfect.
    """
    )
