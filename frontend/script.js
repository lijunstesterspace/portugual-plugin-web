document.getElementById('parse-button').addEventListener('click', parseInput);
document.getElementById('clear-button').addEventListener('click', clearFields);

function displayMessage(message) {
    const outputDiv = document.getElementById('output');
    outputDiv.textContent = message;
}

async function parseInput() {
    const inputText = document.getElementById('inputText').value;

    if (!inputText.trim()) {
        alert('Input is empty!');
        return;
    }

    displayMessage('Loading...');

    try {
        const response = await fetch('/parse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input: inputText }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            displayMessage(`Error: ${errorData.error || 'Unknown error'}`);
            return;
        }

        const parsedData = await response.json();
        displayMessage(JSON.stringify(parsedData || {}, null, 2));
    } catch (error) {
        console.error('Error parsing input:', error);
        displayMessage('An error occurred!');
    }
}

function clearFields() {
    document.getElementById('inputText').value = '';
    displayMessage('');
}
