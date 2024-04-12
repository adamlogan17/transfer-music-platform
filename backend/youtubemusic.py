from google_auth_oauthlib.flow import InstalledAppFlow
import requests
from googleapiclient.discovery import build


def get_auth_url():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['https://www.googleapis.com/auth/youtube']
    )

    flow.redirect_uri = "http://localhost:5173"

    authorization_url = flow.authorization_url(prompt='consent')[0]

    return authorization_url


def get_access_token(code):
    """I am not sure how to get the flow stuff working without having this as direclty as the docs just have 'auth"""
    # flow = InstalledAppFlow.from_client_secrets_file(
    #     'client_secrets.json',
    #     scopes=['https://www.googleapis.com/auth/drive.metadata.readonly'],
    #     state=state)
    # flow.redirect_uri = "http://localhost:5173"
    # return flow.fetch_token(authorization_response="")

    url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': '1085278954549-u6n0taobjic83ot0ia056o7rnkhv8284.apps.googleusercontent.com',
        'client_secret': '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',
        'redirect_uri': 'http://localhost:5173',
        'grant_type': 'authorization_code'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    return requests.post(url, data=data, headers=headers).json()['access_token']

def get_playlists(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}

    return requests.get("https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics%2C%20id&part=id&mine=true", headers=headers).json()

if __name__ == '__main__':
    auth_url = get_auth_url()
    print(auth_url)

    code= input("Please enter code: ")

    access_token = get_access_token(code)

    print(access_token)

    playlists = get_playlists(access_token)

    print(playlists)
