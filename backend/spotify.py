from os import environ
import urllib.parse
import base64
import requests
import copy
from dotenv import load_dotenv
from util import *
import threading

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

def getPlaylistTracks(playlistId, accessToken, totalTracks=None, fields='items(track(album,id,name,track_number,artists,href,external_urls,external_ids,uri)'):
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

# TODO Maybe add an additional 'fuzzy search' to filter spotifies own search results rather than taking the first one
def addTracksToPlaylist(playlistId, tracks, accessToken, albumNamePath=['album'], trackNamePath=['track'], artistPath=['artist'], isrcPath=None, order=False):
    headers = {
        'Authorization': f'Bearer {accessToken}'
    }

    uriOfTracks = []
    maxTracksThatCanBeAdded = 50

    uriOfTracks = multiThreadRequest(lambda offset: spotifyTrackSearch(getNestedItem(tracks[offset], trackNamePath), getNestedItem(tracks[offset], artistPath), getNestedItem(tracks[offset], albumNamePath), accessToken)[0]['uri'], 1, len(tracks))

    multiThreadRequest(lambda offset: requests.post(f'{BASEURI}/playlists/{playlistId}/tracks', headers=headers, json={'uris': uriOfTracks[offset:offset + maxTracksThatCanBeAdded]}), maxTracksThatCanBeAdded, len(uriOfTracks))
        

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
        addTracksToPlaylist(newPlaylistId, tracks, accessToken, albumNamePath=['album','name'], trackNamePath=['name'], artistPath=['artists', 0])

def spotifyTrackSearch(trackName, artistName, albumName, accessToken, isrc=None, market='GB'):
    if __name__ == '__main__':
        print("Started searching for track ", trackName)

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
    results = requests.get(url, headers=headers).json()['tracks']['items']
    print(f"Finished searching for track {results[0]['name']}")
    return results

if __name__ == '__main__':
    PERSONAL_ACCESS_TOKEN = environ.get('SPOTIFY_PERSONAL_ACCESS_TOKEN')

    tracks = [
        {
            'track': 'The Less I know the better',
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

    allPlaylists = getAllPlaylists(PERSONAL_ACCESS_TOKEN)
    
    createPlaylist('unordered playlist', PERSONAL_ACCESS_TOKEN, tracks=allPlaylists[0]['tracks'])