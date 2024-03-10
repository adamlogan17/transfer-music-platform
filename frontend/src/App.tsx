import { useState } from 'react';
import axios from 'axios';

function App() {
	const [response, setResponse] = useState('');

	async function callApi() {
		try {
			const result = await axios.get('http://localhost:5000/api');
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
