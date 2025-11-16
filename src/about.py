import streamlit as st
import requests

def about_app():
    st.markdown("**Welcome**")
    st.markdown(
        """
    This simple application allows you to review your Spotify listening activity and search Bandcamp, which pays artists fairly for their music.

    This app will help you identify which tracks and albums you should think about buying.
            
    ### How to use this app:
    1. **Log in with Spotify:** You'll need to grant permission to access your Spotify listening data.
    2. **Explore your top music:** View your top tracks, albums, and artists over short, medium, or long-term periods.
    3. **Generate Bandcamp links:** Press 'Search Bandcamp' to create search links for your favorite tracks, albums, and artists.
    4. **Support artists:** Consider purchasing music from the Bandcamp links to directly support the artists you love.

    ### Important limitations:
    1. **Spotify API limits:** Only 25 users can access this app via Spotify's API. Please request access using the form below if needed.
    2. **Bandcamp search links:** Bandcamp does not allow web scraping. The URLs generated are search result links, not direct links to a track or album page. Please note not all music will be on Bandcamp, so search results won't be perfect.
        
    """
    )
    with st.expander("Request access"):
        with st.form("contact_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            submitted = st.form_submit_button("Send Request")

        if submitted:
            if not name or not email:
                st.warning("Please fill in both your name and email.")
            else:
                try:
                    token = st.secrets["github"]["GITHUB_TOKEN"]
                    repo = st.secrets["github"]["GITHUB_REPO"]
                    url = f"https://api.github.com/repos/{repo}/issues"

                    issue_data = {
                        "title": f"Spotify App Access Request from {name}",
                        "body": f"**Name:** {name}\n**Email:** {email}",
                    }

                    headers = {"Authorization": f"token {token}"}

                    response = requests.post(url, json=issue_data, headers=headers)

                    if response.status_code == 201:
                        st.success(
                            f"Thanks {name}! Your request has been submitted as a GitHub issue."
                        )
                    else:
                        st.error(f"Failed to create GitHub issue: {response.text}")

                except Exception as e:
                    st.error(f"Error: {e}")
