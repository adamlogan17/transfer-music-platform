import { useState } from 'react';
import axios from 'axios';

function App() {
	const [response, setResponse] = useState('');

  const apiUrl:string = import.meta.env.VITE_APP_API_URL;

	async function callApi() {
		try {
			const result = await axios.get(`${apiUrl}/api`);
			setResponse(result.data);
		} catch (error) {
			console.error('Error fetching data', error);
		}
	}

	return (
		<>
			<button onClick={() => callApi()}>Call API</button>

			{response !== undefined && <p>{response.email}</p>}
		</>
	);
}

export default App;
