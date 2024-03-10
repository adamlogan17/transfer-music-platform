import json
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="http://localhost:5173")

@app.route('/api')
def index():
    return jsonify({'name': 'alice',
                       'email': 'alice@outlook.com'})
app.run()