var totalLines = 77;
var lineNumber;
var randomMessageId;
const filePath = "./batería de ideas ingeniosas.txt";

export function getRandomMessage(){
    lineNumber = Math.floor(Math.random() * totalLines)
    fetch(filePath)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.text();
        })
        .then(data => {
            const lines = data.split('\n');
            const line = lines[lineNumber - 1];  // Line numbers are typically 1-based
            randomMessageId = document.getElementById("randomMessage");
            if (randomMessageId)
                randomMessageId.innerHTML = line !== undefined ? line : "This is not an error";
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

