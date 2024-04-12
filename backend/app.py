import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from os import environ
import urllib.parse
import base64
import requests
import copy
from spotify import get_access_token, get_all_playlists, multiRequest, create_playlist, spotify_login

app = Flask(__name__)
CORS(app, origins="http://localhost:5173")

SPOTIFY_CLIENT_ID = environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = environ.get('SPOTIFY_CLIENT_SECRET')
REDIRECT_SITE = environ.get('REDIRECT_SITE')

print(SPOTIFY_CLIENT_ID)

@app.route('/api', methods=['GET'])
def test():
    return jsonify({'name': 'alice',
                        'email': 'alice@outlook.com'})

@app.route('/spotify/login-page', methods=['GET'])
def spotifyLoginEndpoint():
    return jsonify({'url' : spotify_login() })

# change to POST and send code in body
@app.route('/spotify/access-token/<code>', methods=['GET'])
def getAccessTokenEndpoint(code):
    return get_access_token(code)

# https://developer.spotify.com/documentation/web-api/reference/get-list-users-playlists
@app.route('/spotify/all-playlists', methods=['GET'])
def getAllPlaylistsEndpoint():
    accessToken = request.headers.get('Authorization').split()[1]
    if not accessToken:
        return jsonify({'error': 'No access token provided'}), 401
    

    return jsonify({'playlists': get_all_playlists(accessToken)})

# Need to call playlist endpoint to check for total number of tracks, need to see if this already just gives all tracks (if not continue with skelton below)
# app.route('/spotify/playlist-tracks/<playlistId>', methods=['GET'])
# def getAllPlaylistTracks(playlistId):
#     accessToken = request.headers.get('Authorization').split()[1]
#     if not accessToken:
#         return jsonify({'error': 'No access token provided'}), 401
    
#     return jsonify({'tracks': getPlaylistTracks(playlistId, totalPlaylistTracks, accessToken)})

@app.route('/spotify/create-playlist', methods=['POST'])
def createPlaylistEndpoint():
    accessToken = request.headers.get('Authorization').split()[1]
    if not accessToken:
        return jsonify({'error': 'No access token provided'}), 401
    
    return create_playlist(accessToken)

app.run()