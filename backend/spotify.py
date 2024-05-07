from os import environ
import urllib.parse
import base64
import requests
import copy
from dotenv import load_dotenv
import util

load_dotenv()
SPOTIFY_CLIENT_ID = environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_SITE = environ.get("REDIRECT_SITE")

BASEURI = "https://api.spotify.com/v1"

# TODO Make sure to add proper error handling, as spotify returns {'error': 'message'} so return this message like f'ERROR: {response['error']}'


def spotify_login():
    state = "HMFLKIUERNFKLJUR"
    scope = "user-read-currently-playing playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-read-recently-played user-library-modify user-read-private"

    params = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": SPOTIFY_CLIENT_ID,
            "scope": scope,
            "redirect_uri": REDIRECT_SITE,
            "state": state,
        }
    )

    return f"https://accounts.spotify.com/authorize?{params}"


def get_access_token(code):
    auth_header = base64.b64encode(
        f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode("utf-8")
    ).decode("utf-8")

    auth_options = {
        "url": "https://accounts.spotify.com/api/token",
        "data": {
            "code": code,
            "redirect_uri": REDIRECT_SITE,
            "grant_type": "authorization_code",
        },
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_header}",
        },
    }

    # the '**' unpacks the dictionary into keyword arguments
    return requests.post(**auth_options).json()


def get_all_playlists(accessToken):
    MAXRETURNEDPLAYLISTS = 50

    headers = {"Authorization": f"Bearer {accessToken}"}

    initial_response = requests.get(
        f"{BASEURI}/me/playlists?limit={MAXRETURNEDPLAYLISTS}", headers=headers
    ).json()

    try:
        total_playlists = initial_response["total"]
    except KeyError:
        return initial_response

    all_playlists = initial_response["items"].extend(
        util.multi_request(
            "{BASEURI}/me/playlists",
            MAXRETURNEDPLAYLISTS,
            total_playlists,
            headers,
            start_offset=1,
        )
    )

    all_playlists = get_multiple_playlists_tracks(
        initial_response["items"], accessToken
    )

    return all_playlists


def get_multiple_playlists_tracks(initial_playlists, access_token):
    playlists = copy.deepcopy(initial_playlists)
    for playlist in playlists:
        if __name__ == "__main__":
            print(playlist["name"], playlist["id"])

        playlist["tracks"] = get_playlist_tracks(
            playlist["id"], access_token, total_tracks=playlist["tracks"]["total"]
        )
    return playlists


def get_playlist_tracks(
    playlistId,
    accessToken,
    total_tracks=None,
    fields="items(track(album,id,name,track_number,artists,href,external_urls,external_ids,uri)",
):
    MAXRETURNEDTRACKS = 50
    headers = {"Authorization": f"Bearer {accessToken}"}

    if not total_tracks:
        try:
            total_tracks = requests.get(
                f"{BASEURI}/playlists/{playlistId}?fields=tracks(total)",
                headers=headers,
            ).json()["tracks"]["total"]
        except KeyError:
            return "ERROR: Playlist does not exist"

    all_tracks = [
        track["track"]
        for track in util.multi_request(
            f"{BASEURI}/playlists/{playlistId}/tracks?fields={fields}",
            MAXRETURNEDTRACKS,
            total_tracks,
            headers,
        )
    ]

    return all_tracks


# TODO Maybe add an additional 'fuzzy search' to filter spotifies own search results rather than taking the first one
# TODO Maybe add in the ability were it adds the tracks in the order they are recieved (due to threads being used it is unordered)
def add_tracks_to_playlist(
    playlist_id,
    tracks,
    access_token,
    album_name_path=["album"],
    track_name_path=["track"],
    artist_path=["artist"],
    isrc_path=None,
    order=True,
):
    headers = {"Authorization": f"Bearer {access_token}"}

    max_tracks_that_can_be_added = 50

    uri_of_tracks = util.multi_thread_request(
        lambda offset: spotify_track_search(
            util.get_nested_item(tracks[offset], track_name_path),
            util.get_nested_item(tracks[offset], artist_path),
            util.get_nested_item(tracks[offset], album_name_path),
            access_token,
        )[0],
        1,
        len(tracks),
    )

    for i in range(0, len(uri_of_tracks)):
        print(uri_of_tracks[i]["name"])
        uri_of_tracks[i] = uri_of_tracks[i]["uri"]

    call_fit = len(uri_of_tracks) / max_tracks_that_can_be_added
    num_of_calls = int(call_fit) if call_fit.is_integer() else int(call_fit) + 1

    if order:
        for i in range(0, num_of_calls):
            offset = i * max_tracks_that_can_be_added
            requests.post(
                f"{BASEURI}/playlists/{playlist_id}/tracks",
                headers=headers,
                json={
                    "uris": uri_of_tracks[
                        offset : offset + max_tracks_that_can_be_added
                    ]
                },
            )
    else:
        util.multi_thread_request(
            lambda offset: requests.post(
                f"{BASEURI}/playlists/{playlist_id}/tracks",
                headers=headers,
                json={
                    "uris": uri_of_tracks[
                        offset : offset + max_tracks_that_can_be_added
                    ]
                },
            ),
            max_tracks_that_can_be_added,
            len(uri_of_tracks),
        )


def create_playlist(
    name, accessToken, tracks=None, description="", public=False, order=True
):
    headers = {"Authorization": f"Bearer {accessToken}"}

    body = {"name": name, "description": description, "public": public}

    try:
        userId = requests.get(f"{BASEURI}/me", headers=headers).json()["id"]
    except KeyError:
        return "ERROR: User does not exist"

    try:
        new_playlist_id = requests.post(
            f"{BASEURI}/users/{userId}/playlists", headers=headers, json=body
        ).json()["id"]
    except KeyError:
        return "ERROR: Could not create playlist"

    if tracks:
        add_tracks_to_playlist(
            new_playlist_id,
            tracks,
            accessToken,
            album_name_path=["album", "name"],
            track_name_path=["name"],
            artist_path=["artists", 0],
            order=order,
        )


def spotify_track_search(
    track_name, artist_name, album_name, access_token, isrc=None, market="GB"
):
    if __name__ == "__main__":
        print("Started searching for track ", track_name)

    headers = {"Authorization": f"Bearer {access_token}"}
    query = urllib.parse.quote(
        f"track:{track_name} artist:{artist_name} album:{album_name}"
    )
    search_params = {
        "track": track_name,
        "artist": artist_name,
        "album": album_name,
    }

    if isrc:
        search_params["isrc"] = isrc

    query = urllib.parse.urlencode(search_params)
    url = f"{BASEURI}/search?q={query}&type=track&market={market}"
    results = requests.get(url, headers=headers).json()["tracks"]["items"]
    print(f"Finished searching for track {results[0]['name']}")
    return results


if __name__ == "__main__":
    PERSONAL_ACCESS_TOKEN = environ.get("SPOTIFY_PERSONAL_ACCESS_TOKEN")

    tracks = [
        {
            "track": "The Less I know the better",
            "artist": "Tame Impala",
            "album": "Currents",
        },
        {"track": "Alone No More", "artist": "Philip George", "album": "Alone No More"},
        {
            "track": "Asking For iT",
            "artist": "shinedown",
            "album": "Threat to survival",
        },
    ]

    all_playlists = get_all_playlists(PERSONAL_ACCESS_TOKEN)

    # test = [None for i in range(5, 333)]

    # print(test)
    for playlist in all_playlists:
        if playlist["name"] == "Club":
            create_playlist(
                "checking order (club)",
                PERSONAL_ACCESS_TOKEN,
                tracks=playlist["tracks"],
            )
            break
