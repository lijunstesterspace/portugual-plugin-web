document.getElementById('parseButton').addEventListener('click', async () => {
  const inputString = document.getElementById('inputString').value;

  try {
    const response = await fetch('http://127.0.0.1:5000/parse', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ string: inputString }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const result = await response.json();
    document.getElementById('result').textContent = JSON.stringify(result, null, 2);
  } catch (error) {
    console.error('Error:', error);
    document.getElementById('result').textContent = `Error: ${error.message}`;
  }
});
