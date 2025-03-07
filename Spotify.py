import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import requests

SPOTIPY_CLIENT_ID = 'ad190b91270542a099edfb47ec8d6f16'
SPOTIPY_CLIENT_SECRET = '7b0bf63ac1294d69839c7f0289446318'
REDIRECT_URI = 'http://localhost/'

NOTION_API_KEY = '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'
DATABASE_ID = '1922fd69bbbd80c68353f2addbc1a40e'
url = f'https://api.notion.com/v1/pages'

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

scope = 'user-library-read'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
))

def list_songs_in_first_playlist():
    # Fetch the current user's playlists
    results = sp.current_user_playlists(limit=50)
    playlists = results['items']
    
    if playlists:
        # Get the first playlist
        first_playlist = playlists[0]
        playlist_id = first_playlist['id']
        print(f"First playlist: {first_playlist['name']} (ID: {playlist_id})")
        
        # Fetch the tracks from the first playlist
        results = sp.playlist_tracks(playlist_id)
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        
        # Print the tracks with numbering and add to Notion database
        for idx, item in enumerate(tracks):
            track = item['track']
            song_name = track['name']
            artist_name = ", ".join([artist['name'] for artist in track['artists']])
            spotify_link = track['external_urls']['spotify']
            print(f"{idx + 1}. {song_name} by {artist_name} (Link: {spotify_link})")
            if not song_exists_in_notion(song_name, artist_name):
                add_song_to_notion(song_name, artist_name, spotify_link)
            else:
                update_spotify_link_if_missing(artist_name, spotify_link)
    else:
        print("No playlists found.")

def song_exists_in_notion(song_name, artist_name):
    query_url = f'https://api.notion.com/v1/databases/{DATABASE_ID}/query'
    query_payload = {
        "filter": {
            "and": [
                {
                    "property": "Song",
                    "title": {
                        "equals": song_name
                    }
                },
                {
                    "property": "Artist",
                    "rich_text": {
                        "equals": artist_name
                    }
                }
            ]
        }
    }
    response = requests.post(query_url, headers=headers, json=query_payload)
    if response.status_code == 200:
        results = response.json()
        return len(results['results']) > 0
    else:
        print(f"Failed to query Notion database. Status code: {response.status_code}, Response: {response.text}")
        return False

def update_spotify_link_if_missing(artist_name, spotify_link):
    query_url = f'https://api.notion.com/v1/databases/{DATABASE_ID}/query'
    query_payload = {
        "filter": {
            "property": "Artist",
            "rich_text": {
                "equals": artist_name
            }
        }
    }
    response = requests.post(query_url, headers=headers, json=query_payload)
    if response.status_code == 200:
        results = response.json()
        if len(results['results']) > 0:
            page_id = results['results'][0]['id']
            properties = results['results'][0]['properties']
            if 'Spotify Link' not in properties or not properties['Spotify Link']['url']:
                update_url = f'https://api.notion.com/v1/pages/{page_id}'
                update_payload = {
                    "properties": {
                        "Spotify Link": {
                            "url": spotify_link
                        }
                    }
                }
                update_response = requests.patch(update_url, headers=headers, json=update_payload)
                if update_response.status_code == 200:
                    print(f"Updated Spotify link for {artist_name}.")
                else:
                    print(f"Failed to update Spotify link for {artist_name}. Status code: {update_response.status_code}, Response: {update_response.text}")
    else:
        print(f"Failed to query Notion database. Status code: {response.status_code}, Response: {response.text}")

def add_song_to_notion(song_name, artist_name, spotify_link):
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Song": {
                "title": [
                    {
                        "text": {
                            "content": song_name
                        }
                    }
                ]
            },
            "Artist": {
                "rich_text": [
                    {
                        "text": {
                            "content": artist_name
                        }
                    }
                ]
            },
            "Spotify Link": {
                "url": spotify_link
            }
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Added {song_name} by {artist_name} to Notion.")
    else:
        print(f"Failed to add {song_name} by {artist_name} to Notion. Status code: {response.status_code}, Response: {response.text}")

# List all songs in the first playlist and add them to the Notion database
list_songs_in_first_playlist()