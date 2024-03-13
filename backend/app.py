import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from os import environ
import urllib.parse
import base64
import requests
import copy

app = Flask(__name__)
CORS(app, origins="http://localhost:5173")

SPOTIFY_CLIENT_ID = environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = environ.get('SPOTIFY_CLIENT_SECRET')
REDIRECT_SITE = environ.get('REDIRECT_SITE')

@app.route('/api', methods=['GET'])
def test():
    return jsonify({'name': 'alice',
                        'email': 'alice@outlook.com'})

@app.route('/spotify/login-page', methods=['GET'])
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
    
    return jsonify({'url' : f'https://accounts.spotify.com/authorize?{params}'})

# change to POST and send code in body
@app.route('/spotify/access-token/<code>', methods=['GET'])
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

# https://developer.spotify.com/documentation/web-api/reference/get-list-users-playlists
@app.route('/spotify/all-playlists', methods=['GET'])
def getAllPlaylists():
    accessToken = request.headers.get('Authorization').split()[1]
    if not accessToken:
        return jsonify({'error': 'No access token provided'}), 401
    maxReturnedPlaylists = 50

    headers = {
        'Authorization': f'Bearer {accessToken}'
    }
    initialResponse = requests.get(f'https://api.spotify.com/v1/me/playlists?limit={maxReturnedPlaylists}', headers=headers).json()
    try:
        totalPlaylists = initialResponse['total']
    except KeyError:
        return jsonify({'error': 'Internal Error'}), 400
    
    allPlaylists = initialResponse['items'].extend(multiRequest('https://api.spotify.com/v1/me/playlists', maxReturnedPlaylists, totalPlaylists, headers, startOffset=1))

    allPlaylists = getMultiplePlaylistsTracks(initialResponse['items'], accessToken)

    return jsonify({'playlists': allPlaylists})

# Need to call playlist endpoint to check for total number of tracks, need to see if this already just gives all tracks (if not continue with skelton below)
# app.route('/spotify/playlist-tracks/<playlistId>', methods=['GET'])
# def getAllPlaylistTracks(playlistId):
#     accessToken = request.headers.get('Authorization').split()[1]
#     if not accessToken:
#         return jsonify({'error': 'No access token provided'}), 401
    
#     return jsonify({'tracks': getPlaylistTracks(playlistId, totalPlaylistTracks, accessToken)})

def getMultiplePlaylistsTracks(initialPlaylists, accessToken):
    playlists = copy.deepcopy(initialPlaylists)

    for playlist in playlists:
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

def multiRequest(endpoint, maxReturned, totalToReturn, headers, startOffset=0, baseKey='items'):
    callFit = totalToReturn / maxReturned
    numOfCalls = int(callFit) if callFit.is_integer() else int(callFit) + 1
    allItems = []

    endpoint += '&' if '?' in endpoint else '?'

    for i in range(startOffset, numOfCalls):
        offset = i * maxReturned
        try:
            response = requests.get(f'{endpoint}offset={offset}&limit={maxReturned}', headers=headers).json()
        except:
            response[baseKey] = f'Error getting for off set: {offset}'
        allItems.extend(response[baseKey])
    return allItems

app.run()