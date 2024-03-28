import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import util

# flow = InstalledAppFlow.from_client_secrets_file(
#     'client_secrets.json',
#     scopes=['https://www.googleapis.com/auth/youtube']
# )

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json',
    scopes=['https://www.googleapis.com/auth/youtube.readonly']
)

flow.run_local_server(port=8000, prompt="consent")

credentials = flow.credentials

print(credentials.to_json())

# youtube = build('youtube', 'v3', developerKey=api_key)

# request = youtube.playlistItems().list(
#     part="status",
#     playlistId="PLBCF2DAC6FFB574DE"
# )

# response = request.execute()

# print(response)
