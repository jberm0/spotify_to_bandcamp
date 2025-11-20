import streamlit as st
import requests


def about_app():
    st.markdown("**Welcome**")
    st.markdown(
        """
    This simple application allows you to review your Spotify listening activity and search Bandcamp, where you can buy music directly from artists and labels.
            
    ### How to use this app:
    1. **Log in with Spotify:** You'll need to grant permission to access your Spotify listening data. You can do this on the 'Login' tab. If you can't log in, you'll probably need to allow this application to access your Spotify account, you can request this below.
    2. **Explore your top music:** View your top tracks, albums, and artists over short, medium, or long-term periods. You can use filters on the left sidebar to search if you like.
    3. **Generate Bandcamp links:** Press 'Search Bandcamp' to create search links for your favorite tracks, albums, and artists. Click the link to go to Bandcamp.
    4. **Support artists:** Consider purchasing music from the Bandcamp links to directly support the artists you love.

    ### Important limitations:
    1. **Spotify API limits:** Only 25 users can access this app via Spotify's API. Please request access using the form below if needed.
    2. **Bandcamp search links:** Bandcamp does not allow web scraping. The URLs generated are search result links, not direct links to a track or album page. Please note not all music will be on Bandcamp, so search results won't be perfect.
    """
    )
    st.subheader("Request Access")

    with st.expander("Access Form"):
        st.write("Submitting this form will provide the details needed to add your Spotify account to the application user list. Due to Spotify's API limits this is manual :/")
        with st.form("contact_form"):
            name = st.text_input("Your Name", help="Access is limited to 25 people, so I'd like to know who I'm sharing with")
            email = st.text_input("Your Email", help="This must be the email used for your Spotify account")
            submitted = st.form_submit_button("Send Request")

        if submitted:
            name = name.strip()
            email = email.strip()
            if not name or not email:
                st.warning("Please fill in both your name and email.")
                return

            if "@" not in email or "." not in email:
                st.warning("Please enter a valid email address.")
                return

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
                        f"Thanks {name}! Your request has been submitted."
                    )
                else:
                    st.error(
                        f"Failed to create GitHub issue. Please try again later."
                    )

            except Exception as e:
                st.error("An unexpected error occurred. Please try again later.")
