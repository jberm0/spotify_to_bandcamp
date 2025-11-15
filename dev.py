import urllib.parse
import webbrowser


def search_bandcamp_link(artist, album, track):
    query = f"{artist} {album} {track} site:bandcamp.com"
    url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
    return url


def bandcamp_search(artist, album, track):
    query = f"{artist} {track}"
    encoded = urllib.parse.quote(query)
    return f"https://bandcamp.com/search?q={encoded}"

link = bandcamp_search(
    "Black Country, New Road",
    "Forever Howlong",
    "For the Cold Country",
)

# link = search_bandcamp_link(
#     "Payfone",
#     "Volt to Volt (Radio Edit)",
#     "Volt to Volt (Radio Edit)",
# )
print(link)
