document.getElementById('userInfoForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent the default form submission
    const username = document.getElementById('username').value;

    fetch(`/user_info/get_user_info?username=${username}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('result').textContent = 'Error: ' + data.error;
            } else {
                document.getElementById('result').textContent = `Username: ${data.username}, Alias: ${data.alias}, Online: ${data.online}, Wins: ${data.wins}, Loses: ${data.loses}, Punctuation: ${data.punctuation}, Has Photo Profile: ${data.has_photo_profile}`;
            }
        })
        .catch(error => {
            document.getElementById('result').textContent = 'Failed to fetch user info: ' + error;
        });
});
