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

BASEURI = 'https://api.spotify.com/v1'

# TODO Make sure to add proper error handling, as spotify returns {'error': 'message'} so return this message like f'ERROR: {response['error']}'

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

    # the '**' unpacks the dictionary into keyword arguments
    return requests.post(**auth_options).json()

def getAllPlaylists(accessToken):
    MAXRETURNEDPLAYLISTS = 50

    headers = {
        'Authorization': f'Bearer {accessToken}'
    }
    initialResponse = requests.get(f'{BASEURI}/me/playlists?limit={MAXRETURNEDPLAYLISTS}', headers=headers).json()
    try:
        totalPlaylists = initialResponse['total']
    except KeyError:
        return initialResponse
    
    allPlaylists = initialResponse['items'].extend(multiRequest('{BASEURI}/me/playlists', MAXRETURNEDPLAYLISTS, totalPlaylists, headers, startOffset=1))

    allPlaylists = getMultiplePlaylistsTracks(initialResponse['items'], accessToken)

    return allPlaylists

def getMultiplePlaylistsTracks(initialPlaylists, accessToken):
    playlists = copy.deepcopy(initialPlaylists)

    for playlist in playlists:
        if __name__ == '__main__':
            print(playlist['name'], playlist['id'])

        playlist['tracks'] = getPlaylistTracks(playlist['id'], accessToken, totalTracks=playlist['tracks']['total'])
    return playlists

def getPlaylistTracks(playlistId, accessToken, totalTracks=None, fields='items(track(album,id,name,track_number,artists,href,external_urls,external_ids)'):
    MAXRETURNEDTRACKS = 50
    headers = {
        'Authorization': f'Bearer {accessToken}'
    }

    if not totalTracks:
        try:
            totalTracks = requests.get(f'{BASEURI}/playlists/{playlistId}?fields=tracks(total)', headers=headers).json()['tracks']['total']
        except KeyError:
            return 'ERROR: Playlist does not exist'

    allTracks = [track['track'] for track in multiRequest(f'{BASEURI}/playlists/{playlistId}/tracks?fields={fields}', MAXRETURNEDTRACKS, totalTracks, headers)]
    return allTracks

# TODO fix the issue were the max tracks that can be added to a playlist is 100
def addTracksToPlaylist(playlistId, tracks, accessToken):
    headers = {
        'Authorization': f'Bearer {accessToken}'
    }

    uriOfTracks = []

    for track in tracks:
        try:
            uriOfTracks.append(track['uri'])
        except KeyError:
            uriOfTracks.append(spotifyTrackSearch(track['track'], track['artist'], track['album'], accessToken)[0]['uri'])

    requests.post(f'{BASEURI}/playlists/{playlistId}/tracks', headers=headers, json={'uris': uriOfTracks})

def createPlaylist(name, accessToken, tracks=[], description='', public=False):
    headers = {
        'Authorization': f'Bearer {accessToken}'
    }

    body = {
        'name': name,
        'description': description,
        'public': public
    }

    try:
        userId = requests.get(f'{BASEURI}/me', headers=headers).json()['id']
    except KeyError:
        return 'ERROR: User does not exist'
    
    try:
        newPlaylistId = requests.post(f'{BASEURI}/users/{userId}/playlists', headers=headers, json=body).json()['id']
    except KeyError:
        return 'ERROR: Could not create playlist'
    
    if tracks:
        addTracksToPlaylist(newPlaylistId, tracks, accessToken)

def spotifyTrackSearch(trackName, artistName, albumName, accessToken, isrc=None, market='GB'):
    headers = {
        'Authorization': f'Bearer {accessToken}'
    }
    query = urllib.parse.quote(f'track:{trackName} artist:{artistName} album:{albumName}')
    searchParams = {
        'track': trackName,
        'artist': artistName,
        'album': albumName,
    }

    if isrc:
        searchParams['isrc'] = isrc

    query = urllib.parse.urlencode(searchParams)
    url = f'{BASEURI}/search?q={query}&type=track&market={market}'
    return requests.get(url, headers=headers).json()['tracks']['items']

if __name__ == '__main__':
    PERSONAL_ACCESS_TOKEN = environ.get('SPOTIFY_PERSONAL_ACCESS_TOKEN')
    running = '6lXye8XgLjOcLaxejerfnc'
    recommended = '0qcIskGBpBWmKKlbUxzJpF'
    # allPlaylists = createPlaylist("py works", PERSONAL_ACCESS_TOKEN)
    # print(allPlaylists)

    tracks = [
        {
            'track': 'The Less I Know The Better',
            'artist': 'Tame Impala',
            'album': 'Currents'
        },
        {
            'track': 'Alone No More',
            'artist': 'Philip George',
            'album': 'Alone No More'
        },
        {
            'track': 'Asking For iT',
            'artist': 'shinedown',
            'album': 'Threat to survival'
        }
    ]

    createPlaylist('py works 2', PERSONAL_ACCESS_TOKEN, tracks=tracks)