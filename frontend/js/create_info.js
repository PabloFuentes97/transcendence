document.getElementById('createUserInfoForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent the default form submission

    const username = document.getElementById('username').value;
    const alias = document.getElementById('alias').value || username; // Use username as alias if not provided

    const data = JSON.stringify({
        username: username,
        alias: alias
    });

    fetch('/user_info/create_user_info', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: data
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('result').textContent = 'Error: ' + data.error;
        } else {
            document.getElementById('result').textContent = data.Correct;
        }
    })
    .catch(error => {
        document.getElementById('result').textContent = 'Failed to create user info: ' + error;
    });
});
