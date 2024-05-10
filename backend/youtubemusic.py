import threading
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
from Types import Playlist, Image, Song

BASEURI = "https://youtube.googleapis.com/youtube/v3"


def get_auth_url():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['https://www.googleapis.com/auth/youtube']
    )

    flow.redirect_uri = "http://localhost:5173"

    authorization_url = flow.authorization_url(prompt='consent')[0]

    return authorization_url


def get_access_token(code):
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


def retrieve_album_name(description):
    """
    The album name appears after the second set of 2 new line characters, within the description and
    the below filters this out
    """
    count = 0
    album = ""
    for i in range(1, len(description)):
        if description[i - 1] == '\n' and description[i] == '\n':
            count += 1
        if count == 2:
            album += description[i]
    # need to remove the first and last characters of the string as these are new line characters
    album = album[1:-1]

    return album


def extract_song(video, song_identifier=' - Topic'):
    # TODO Maybe make song_identifier a global variable as it is used in multiple places and always needs to be the same
    artist = ''
    title = video['snippet']['title']

    # When searching the artist is stored within channelTitle but if retrieved from a playlist
    # it is within 'videoOwnerChannelTitle
    try:
        artist = video['snippet']['videoOwnerChannelTitle'][:-len(song_identifier)]
    except KeyError:
        artist = video['snippet']['channelTitle'][:-len(song_identifier)]
    album = retrieve_album_name(video['snippet']['description'])
    return Song(title, album, artist, "")


def get_playlist_songs(access_token, playlist_id):
    """Returns an array of Songs that are in the playlist"""
    headers = {"Authorization": f"Bearer {access_token}"}

    # It appears YouTube identifies if a video is a 'song' is by the string below being contained within the
    # video owner channel
    song_identifier = ' - Topic'

    url = f"{BASEURI}/playlistItems?part=contentDetails,snippet&maxResults=50&playlistId={playlist_id}"

    videos = youtube_multi_request(url, headers)

    songs = []

    for video in videos:
        if video['snippet']['videoOwnerChannelTitle'].endswith(song_identifier):
            songs.append(extract_song(video, song_identifier=song_identifier))

    return songs


def get_playlists(access_token):
    """
    It is important to note that the account must be a YouTube channel rather than a generic account for the API
    to return the playlist IDs.
    Due to the use of the 'nextPageToken' the multiRequest function cannot be used to fetch all the playlists, but
    threads are used to allow the songs to be fetched in the background, to speed up the process.
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    url = f"{BASEURI}/playlists?part=id,contentDetails,snippet&mine=true&maxResults=50"

    all_playlist_info = youtube_multi_request(url, headers, thread_task=lambda playlists, index: filter_playlists(playlists, index, access_token))

    filtered_playlist = []

    for playlist in all_playlist_info:
        # Only add playlists that have songs within them
        if len(playlist['songs']) > 0:
            filtered_playlist.append(Playlist(
                playlist['id'],
                [Image(image['url'], image['height'], image['width']) for image in playlist['snippet']['thumbnails'].values()],
                playlist['snippet']['title'],
                playlist['snippet']['description'],
                playlist['songs']
            ))

    return filtered_playlist


def filter_playlists(playlists, playlist_index, access_token):
    playlists[playlist_index]['songs'] = get_playlist_songs(access_token, playlists[playlist_index]['id'])


def youtube_multi_request(url, headers, item_key="items", thread_task=None):
    all_info = []
    all_threads = []
    next_page_token = ""

    # TODO Possibly at some point refactor this loop
    while True:
        amended_url = url
        #
        if next_page_token != "":
            amended_url = f"{url}&pageToken={next_page_token}"
        response = requests.get(amended_url, headers=headers).json()
        try:
            all_items = response[item_key]
            # Allows for tasks to run in the 'background' when a request the next request is being fetched
            # An important thing to note is that the two variables being passed are used to store the information back
            # to the main thread (this is not thread safe, as in theory threads can manipulate the same index but in
            # practice this won't happen if used correct as it is set up to manipulate a different index each time and
            # the fact that the function should only be additive)
            #
            # The main use case for this is to allow the videos, from a playlist to be fetched while the system sends
            # requests to get more playlists
            #
            # (apologies for the long comment)
            if thread_task is not None:
                for i in range(len(all_items)):
                    t = threading.Thread(target=thread_task(all_items, i), args=(all_items, i))
                    t.start()
            all_info.extend(all_items)
            next_page_token = response['nextPageToken']
        except KeyError:
            break

    for t in all_threads:
        t.join()

    return all_info


def search_song(name, artist, album, access_token):
    """
    TODO Maybe remove the album name as it doesn't fit well in the google search
    TODO Maybe add an optional duaration but check this with the 'videoDuration' documentation as this only allows for long, medium and large
    TODO Switch to use multi request
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    query = f"{name} {artist}"

    # This is thr topic ID for music and is used to narrow the search
    # Topic ID's can be found at https://developers.google.com/youtube/v3/docs/search/list
    music_topic_id = "/m/04rlf"

    url = f"{BASEURI}/search?type=video&topicId={music_topic_id}&q={query}"

    response = requests.get(url, headers=headers).json()

    return response['items'][0]['id']['videoId']


def get_video_details(videoIds, access_token):
    """
    TODO Switch to using multi request
    """
    test = ["dd"]

    print(','.join(test))

    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{BASEURI}/videos?part=snippet,contentDetails&id={','.join(videoIds)}"
    response = requests.get(url, headers=headers).json()

    songs = []
    for video in response['items']:
        print(video)
        songs.append(extract_song(video))

    return songs


if __name__ == '__main__':
    # auth_url = get_auth_url()
    # print(auth_url)
    #
    # code= input("Please enter code: ")
    #
    # access_token = get_access_token(code)
    #
    # print(access_token)

    access_token = ""

    playlists = get_playlists(access_token)
    print(playlists)
    print(len(playlists))

    # song = search_song("Outlaw Man - 2013 Remaster", "Eagles", "Desperado", access_token)

    video_details = get_video_details(['0Mu0c2iwC2E'], access_token)

    print(video_details)


