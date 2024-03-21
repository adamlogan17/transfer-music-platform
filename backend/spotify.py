from os import environ
import urllib.parse
import base64
import requests
import copy
from dotenv import load_dotenv
from util import *

load_dotenv()
SPOTIFY_CLIENT_ID = environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = environ.get('SPOTIFY_CLIENT_SECRET')
REDIRECT_SITE = environ.get('REDIRECT_SITE')

def spotifyLogin():
    state = "HMFLKIUERNFKLJUR"
    scope = 'user-read-currently-playing playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-read-recently-played user-library-modify user-read-private'
    
    params = urllib.parse.urlencode({
        'response_type': 'code',
        'client_id': SPOTIFY_CLIENT_ID,
        'scope': scope,
        'redirect_uri': REDIRECT_SITE,
        'state': state
    })
    
    return f'https://accounts.spotify.com/authorize?{params}'

def getAccessToken(code):
    auth_header = base64.b64encode(f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}'.encode('utf-8')).decode('utf-8')

    auth_options = {
        'url': 'https://accounts.spotify.com/api/token',
        'data': {
            'code': code,
            'redirect_uri': REDIRECT_SITE,
            'grant_type': 'authorization_code'
        },
        'headers': {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_header}'
        }
    }

    return requests.post(**auth_options).json()

def getAllPlaylists(accessToken):
    MAXRETURNEDPLAYLISTS = 50

    headers = {
        'Authorization': f'Bearer {accessToken}'
    }
    initialResponse = requests.get(f'https://api.spotify.com/v1/me/playlists?limit={MAXRETURNEDPLAYLISTS}', headers=headers).json()
    try:
        totalPlaylists = initialResponse['total']
    except KeyError:
        return initialResponse
    
    allPlaylists = initialResponse['items'].extend(multiRequest('https://api.spotify.com/v1/me/playlists', MAXRETURNEDPLAYLISTS, totalPlaylists, headers, startOffset=1))

    allPlaylists = getMultiplePlaylistsTracks(initialResponse['items'], accessToken)

    return allPlaylists

def getMultiplePlaylistsTracks(initialPlaylists, accessToken):
    playlists = copy.deepcopy(initialPlaylists)

    for playlist in playlists:
        if __name__ == '__main__':
            print(playlist['name'])

        playlist['tracks'] = getPlaylistTracks(playlist['id'], playlist['tracks']['total'], accessToken)
    return playlists

def getPlaylistTracks(playlistId, totalTracks, accessToken, fields='items(track(album,id,name,track_number,artists,href,external_urls,external_ids)'):
    maxReturnedTracks = 50
    headers = {
        'Authorization': f'Bearer {accessToken}'
    }
    allTracks = [track['track'] for track in multiRequest(f'https://api.spotify.com/v1/playlists/{playlistId}/tracks?fields={fields}', maxReturnedTracks, totalTracks, headers)]
    return allTracks

def createPlaylist(accessToken):
    headers = {
        'Authorization': f'Bearer {accessToken}'
    }

    return spotifyTrackSearch('The Less I Know The Better', 'Tame Impala', 'Currents', accessToken)


def spotifyTrackSearch(trackName, artistName, albumName, accessToken):
    headers = {
        'Authorization': f'Bearer {accessToken}'
    }

    query = urllib.parse.quote(f'track:{trackName} artist:{artistName} album:{albumName}')
    print(query)

    query = urllib.parse.urlencode({
        'track': trackName,
        'artist': artistName,
        'album': albumName
    })

    print(query)

    url = f'https://api.spotify.com/v1/search?q={query}&type=track&market=UK'
    print(url)

    return requests.get(url, headers=headers).json()

if __name__ == '__main__':
    PERSONAL_ACCESS_TOKEN = environ.get('SPOTIFY_PERSONAL_ACCESS_TOKEN')
    allPlaylists = getAllPlaylists(PERSONAL_ACCESS_TOKEN)
    prettyDict(allPlaylists)