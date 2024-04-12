import axios from 'axios';
import { useEffect, useState } from 'react';

async function getPlaylists(accessToken: string|null) {
  const apiUrl: string = import.meta.env.VITE_APP_API_URL;

  console.log(accessToken);

  try {
    const playlists = await axios.get(`${apiUrl}/spotify/all-playlists`, {
      headers: {
        Authorization: `Bearer ${accessToken}`
      }
    })
    console.log(playlists);
    return playlists.data.playlists;
  } catch (error) {
    console.log(error);
    return [];
  }
}

async function createPlaylists(accessToken: string|null) {
  const apiUrl: string = import.meta.env.VITE_APP_API_URL;

  console.log(accessToken);

  try {
    const playlists = await axios.post(`${apiUrl}/spotify/create-playlist`, {
      headers: {
        Authorization: `Bearer ${accessToken}`
      }
    })
    console.log(playlists);
    return playlists.data.playlists;
  } catch (error) {
    console.log(error);
    return [];
  }
}

async function authoriseSpotify() {
	const apiUrl: string = import.meta.env.VITE_APP_API_URL;
  try {
    const result = await axios.get(`${apiUrl}/spotify/login-page`);
    window.location = result.data.url;
  } catch (error) {
    console.log(error);
  }
}

function App() {
  const [playlists, setPlaylists] = useState([]);
  const [spotifyAccessToken, setSpotifyAccessToken] = useState<string|null>(null);

  async function getSpotifyAccessToken() {
    const apiUrl: string = import.meta.env.VITE_APP_API_URL;
  
    try {
      const spotifyAccess = await axios.get(
        `${apiUrl}/spotify/access-token/${new URLSearchParams(window.location.search).get('code')}`
      );
  
      setSpotifyAccessToken(spotifyAccess.data.access_token);
    } catch (error) {
      console.log(error);
      return [];
    }
  }

  useEffect(() => {
    const code = new URLSearchParams(window.location.search).get('code');
    if (code) {
      getSpotifyAccessToken();
    }
  }, []);

	return (
		<>
      <h1>{spotifyAccessToken}</h1>
      {spotifyAccessToken === null || spotifyAccessToken === undefined ? (<button onClick={() => authoriseSpotify()}>Authorise</button>)
      :
      (
        <>
          <button onClick={() =>{
            getPlaylists(spotifyAccessToken).then((playlists) => setPlaylists(playlists))
            createPlaylists(spotifyAccessToken).then((playlists) => alert('done!'))
          }}>Get Playlists</button>

          <ul>
            {
              playlists.length === 0 && <li>Loading...</li>
            }
            {playlists.map((playlist:any) => (
              <li key={playlist.id}>{playlist.name}</li>
            ))}
          </ul>
        </>

      )
      }
		</>
	);
}

export default App;
