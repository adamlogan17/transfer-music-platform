from google_auth_oauthlib.flow import InstalledAppFlow
import requests

import util
from Types import Playlist, Image, Song

from util import put_in_json_file


def get_auth_url():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['https://www.googleapis.com/auth/youtube']
    )

    flow.redirect_uri = "http://localhost:5173"

    authorization_url = flow.authorization_url(prompt='consent')[0]

    return authorization_url


def get_access_token(code):
    url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': '1085278954549-u6n0taobjic83ot0ia056o7rnkhv8284.apps.googleusercontent.com',
        'client_secret': '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',
        'redirect_uri': 'http://localhost:5173',
        'grant_type': 'authorization_code'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    return requests.post(url, data=data, headers=headers).json()['access_token']

def get_playlist_songs(access_token, playlist_id):
    """Returns an array of Songs that are in the playlist"""
    headers = {"Authorization": f"Bearer {access_token}"}

    # It appears YouTube identifies if a video is a 'song' is by the string below being contained within the
    # video owner channel
    song_identifier = ' - Topic'

    videos = requests.get(f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails,snippet&maxResults=50&playlistId={playlist_id}",headers=headers).json()['items']
    songs = []

    for video in videos:
        if video['snippet']['videoOwnerChannelTitle'].endswith(song_identifier):
            title = video['snippet']['title']
            artist = video['snippet']['videoOwnerChannelTitle'][:-len(song_identifier)]

            # The album name appears after the second set of 2 new line characters, within the description and
            # the below filters this out
            description = video['snippet']['description']
            count = 0
            album = ""
            for i in range(1, len(description)):
                if description[i - 1] == '\n' and description[i] == '\n':
                    count += 1
                if count == 2:
                    album += description[i]
            # need to remove the first and last characters of the string as these are new line characters
            album = album[1:-1]
            songs.append(Song(title, album, artist, ""))

    return songs

def get_playlists(access_token):
    """
    It is important to note that the account must be a YouTube channel rather than a generic account for the API
    to return the playlist IDs.
    TODO need to make the playlists, use multi_request, though I might need to modify this or create a new function
    TODO separate out getting the songs from the playlist, into it's own function
    due to the API not using numbers for the offset, but a nextPage keyword
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    url = "https://youtube.googleapis.com/youtube/v3/playlists?part=id,contentDetails,snippet&mine=true&maxResults=50"

    all_playlist_info = requests.get(url, headers=headers).json()

    all_playlist_info = all_playlist_info['items']

    filtered_playlist = []

    for playlist in all_playlist_info:
        songs = get_playlist_songs(access_token, playlist['id'])

        if len(songs) > 0:
            filtered_playlist.append(Playlist(
                playlist['id'],
                [Image(image['url'], image['height'], image['width']) for image in playlist['snippet']['thumbnails'].values()],
                playlist['snippet']['title'],
                playlist['snippet']['description'],
                songs
            ))

    return filtered_playlist


if __name__ == '__main__':
    auth_url = get_auth_url()
    print(auth_url)

    code= input("Please enter code: ")

    access_token = get_access_token(code)

    print(access_token)
    # access_token = ""

    playlists = get_playlists(access_token)
    print(playlists)
    print(len(playlists))

