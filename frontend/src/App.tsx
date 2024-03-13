import axios from 'axios';
import { useEffect, useState } from 'react';

async function getAccessToken() {
  const apiUrl: string = import.meta.env.VITE_APP_API_URL;

  try {
    const spotifyAccess = await axios.get(
      `${apiUrl}/spotify/access-token/${new URLSearchParams(window.location.search).get('code')}`
    );

    localStorage.setItem('spotify_access_token', spotifyAccess.data.access_token);
    return await getPlaylists(spotifyAccess.data.access_token);

  } catch (error) {
  }
}

async function getPlaylists(accessToken: string) {
  const apiUrl: string = import.meta.env.VITE_APP_API_URL;

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

function App() {
	const apiUrl: string = import.meta.env.VITE_APP_API_URL;
  const [playlists, setPlaylists] = useState([]);

  useEffect(() => {
    const code = new URLSearchParams(window.location.search).get('code');
    if (code) {
      getAccessToken().then((playlists) => { setPlaylists(playlists) })
    }
  }, []);

	async function callApi() {
		try {
			const result = await axios.get(`${apiUrl}/spotify/login-page`);
			window.location = result.data.url;
		} catch (error) {
			console.log(error);
		}
	}

	return (
		<>
			<button onClick={() => callApi()}>Call API</button>

      <ul>
        {
          playlists.length === 0 && <li>Loading...</li>
        }
        {playlists.map((playlist:any) => (
          <li key={playlist.id}>{playlist.name}</li>
        ))}
      </ul>
		</>
	);
}

export default App;
