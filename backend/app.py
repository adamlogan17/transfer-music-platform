import json
from flask import Flask, jsonify
from flask_cors import CORS
from os import environ

app = Flask(__name__)
CORS(app, origins="http://localhost:5173")

SPOTIFY_CLIENT_ID = environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = environ.get('SPOTIFY_CLIENT_SECRET')

@app.route('/api')
def index():
    print(SPOTIFY_CLIENT_ID)
    return jsonify({'name': 'alice',
                       'email': 'alice@outlook.com'})
app.run()