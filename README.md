# transfer-music-platform (WIP)

This is a web application to assist in

Currently this is a work in progress (WIP) and therefore many features are not implemented yet. Please have a look at the [TODO](#TODO) section of this README to view what still is required to be completed and other ideas which I have.

If you have any suggestions or comments feel free to contact me through email <adamlogan42@gmail.com>, any ideas/advice would be much appreciated!!

## Resources Used for Development

<https://developers.google.com/youtube/v3/code_samples/code_snippets>

<https://www.youtube.com/watch?v=vQQEaSnQ_bs&t=689s>

<https://www.youtube.com/watch?v=th5_9woFJmk&t=104s>

<https://medium.com/pythoneers/from-spotify-to-youtube-music-how-i-wrote-a-simple-tool-in-python-to-migrate-my-playlists-705e878a7cf0>

<https://developers.google.com/identity/protocols/oauth2/web-server>

## Setting up Environment

### Environment Variables

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
- Maybe make a database table that could act as like a cache and it would have title,album,artist,isrc,(spotify unique ID),(youtube video ID),(deezer unique ID),etc
  - This has the possibility of speeding up the process as db queries should be faster then searching the API, and hopefully iy will be more reliable becuase I can map the correct song IDs accross each platform
  - Not sure though how to verify a song is correct without human intervention, but this may just have to happen
- Documentation
  - Need to improve this README
  - If implementing the above OOP idea, need to create class diagram
  - Need to create flowchart for the db stuff if implementing it (maybe do this)
  - Need to add docstrings to all functions
  - Need to add instructions on how to set up Spotify to use the API
  - Need to complete the section in the README on environment variables
- Need to build frontend (will divide up later as soon as backend is completed)
- Eventually dockerise everything and deploy on the cloud (thinking Azure at the minute)
