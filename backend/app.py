import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from os import environ
import urllib.parse
import base64
import requests

app = Flask(__name__)
CORS(app, origins="http://localhost:5173")

SPOTIFY_CLIENT_ID = environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = environ.get('SPOTIFY_CLIENT_SECRET')
REDIRECT_SITE = environ.get('REDIRECT_SITE')

@app.route('/api', methods=['GET'])
def test():
    print(SPOTIFY_CLIENT_ID)
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
    print("code", code)
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

# need to make sure all playlists are returned (there is a 'total' for number of playlists)
# https://developer.spotify.com/documentation/web-api/reference/get-list-users-playlists
@app.route('/spotify/all-playlists', methods=['GET'])
def getAllPlaylists():
    access_token = request.headers.get('Authorization').split()[1]

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    return requests.get('https://api.spotify.com/v1/me/playlists', headers=headers).json()

app.run()