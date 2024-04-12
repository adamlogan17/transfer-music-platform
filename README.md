# transfer-music-platform

## Resources Used for Development

<https://developers.google.com/youtube/v3/code_samples/code_snippets>

<https://www.youtube.com/watch?v=vQQEaSnQ_bs&t=689s>

<https://www.youtube.com/watch?v=th5_9woFJmk&t=104s>

<https://medium.com/pythoneers/from-spotify-to-youtube-music-how-i-wrote-a-simple-tool-in-python-to-migrate-my-playlists-705e878a7cf0>

<https://developers.google.com/identity/protocols/oauth2/web-server>

## Setting up Environment

### Environment Variables

- SPOTIFY_CLIENT_ID : The ID of the client 

### Authorise Google App

- The server needs to be added as a 'Authorised redirect URI' and has be <http://localhost:5000/> and not <http://localhost:5000>
- When testing, need to go to the OAuth consent screen tab and add the user's email within Test user

## TODOs

- Maybe make think about OOP because all the music platforms should have all the same methods and attributes
  - MusicPlatform would maybe be an interface (think about this) and then the interface itself could be used to call the methods
    - So it would be objectName.getPlaylists and it doesn't matter if it is of class Youtube or Spotify and therefore a transfer_playlists(platform1, platform2) would work, no matter what the platforms are
    - An object of the Youtube class would be a user account so would need to have an attribute of access_token (this would be a requirement from the interface class)
    - Static attributes need to be used for the client secrets and client IDs for the platform
    - Need to double check about static attributes for interfaces, but the redirect site would be good to have as this
