document.getElementById('translateBtn').addEventListener('click', async () => {
  const text = document.getElementById('inputText').value;
  const language = document.getElementById('languageSelect').value;

  if (!text) return alert('Please enter text to translate.');

  // Backend API URL
  const api = 'http://127.0.0.1:8000/translate';

  try {
    const response = await fetch(api, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language })
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();
    document.getElementById('outputText').innerText = data.translation;
  } catch (err) {
    console.error(err);
    alert('Failed to translate. Check console for details.');
  }
});
  