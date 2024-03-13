import axios from 'axios';
import { useEffect, useState } from 'react';

function App() {
	const apiUrl: string = import.meta.env.VITE_APP_API_URL;
  const [playlists, setPlaylists] = useState([]);

  async function getAccessToken() {
    const apiUrl: string = import.meta.env.VITE_APP_API_URL;
  
    try {
      const spotifyAccess = await axios.get(
        `${apiUrl}/spotify/access-token/${new URLSearchParams(window.location.search).get('code')}`
      );
  
      console.log(spotifyAccess);
  
      localStorage.setItem('spotify_access_token', spotifyAccess.data.access_token);
      console.log(spotifyAccess.data.access_token);
      getPlaylists(spotifyAccess.data.access_token);
  
    } catch (error) {
      console.log(error);
    }
  }

  function getPlaylists(accessToken: string) {
    console.log("foo", accessToken);
    const apiUrl: string = import.meta.env.VITE_APP_API_URL;
  
    axios.get(`${apiUrl}/spotify/all-playlists`, {
      headers: {
        Authorization: `Bearer ${accessToken}`
      }
    }).then((response) => {
      console.log(response);
      setPlaylists(response.data.items);
    }).catch((error) => {
      console.log(error);
    });
  }

  useEffect(() => {
    const code = new URLSearchParams(window.location.search).get('code');
    if (code) {
      getAccessToken();
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
