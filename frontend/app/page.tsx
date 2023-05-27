'use client'
import { useState, FormEvent } from 'react';
import { PlayCircle } from 'react-feather';

export default function Home(): JSX.Element {
  const [textInput, setTextInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState('');

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();

    const apiUrl = 'https://text2flix.loca.lt/predict';
    const data = { text: textInput.trim() };

    if (data.text) {
      try {
        setLoading(true);

        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });

        if (!response.ok) {
          throw new Error('Error: ' + response.status);
        }

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);

        setAudioUrl(audioUrl);
      } catch (error) {
        console.error('Error:', error);
        // Error handling
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <header className="flex items-center mb-8">
        <PlayCircle size={32} className="mr-2 text-blue-500" />
        <h1 className="text-4xl font-bold text-blue-500 tracking-wider">Text2Flix</h1>
      </header>
      <form onSubmit={handleSubmit} className="flex flex-col">
        <textarea
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-l focus:outline-none resize-none w-80 h-40 text-gray-800 mb-4"
        />
        {loading ? (
          <button type="submit" disabled className="px-4 py-2 bg-blue-500 text-white rounded opacity-50 cursor-not-allowed">
            Loading...
          </button>
        ) : (
          <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none">
            Submit
          </button>
        )}
        {audioUrl && (
          <audio controls src={audioUrl} className="mt-4" />
        )}
      </form>
    </div>
  );
}
