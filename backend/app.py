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

    allPlaylists = getPlaylistTracks(accessToken, initialResponse['items'])

    callFit = totalPlaylists / maxReturnedPlaylists
    numOfCalls = int(callFit) if callFit.is_integer() else int(callFit) + 1

    for i in range(1, numOfCalls):
        offset = i * maxReturnedPlaylists
        response = requests.get(f'https://api.spotify.com/v1/me/playlists?offset={offset}&limit={maxReturnedPlaylists}', headers=headers).json()
        addTracks = getPlaylistTracks(accessToken, response['items'])
        allPlaylists.extend(addTracks)

    return jsonify({'playlists': allPlaylists})

def getPlaylistTracks(accessToken, initialPlaylists):
    playlists = copy.deepcopy(initialPlaylists)

    maxReturnedTracks = 50
    headers = {
        'Authorization': f'Bearer {accessToken}'
    }
    for playlist in playlists:
        print(playlist['name'])
        callFit = playlist['tracks']['total'] / maxReturnedTracks
        numOfCalls = int(callFit) if callFit.is_integer() else int(callFit) + 1
        allTracks = []

        for i in range(0, numOfCalls):
            offset = i * maxReturnedTracks
            try:
                tracksResponse = requests.get(f'{playlist['tracks']['href']}/?offset={offset}&limit={maxReturnedTracks}&fields=items(track(album,id,name,track_number,artists,href,external_urls,external_ids))', headers=headers).json()
                allTracks.extend(tracksResponse['items'])
            except:
                print("Error getting tracks for playlist: ", playlist['name'])
        
        playlist['trackInfo'] = allTracks
    return playlists


app.run()