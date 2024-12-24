// Start a new game
function startGame() {

    
    updateLeaderboard()
    const iframe = document.getElementById('myIframe');
     // iframe.style.display = 'none';

    username = document.getElementById('username').value;
    if (!username) {
        showAlert('Please enter your name.');
        return;
    }
    else if (!isNameValid(username)) {
        showAlert('You are not on the Approved list of Fouhy players.');
        return;
    }

    const categoryDropdown = document.getElementById('categoryDropdown');
    const selectedCategory = categoryDropdown.value;
    console.log(selectedCategory);
    if (!selectedCategory) {
        showAlert('Please select a category.');
        return;
    }

    const header = document.getElementById('heading');
    header.style.display = 'block';

    // const game_header = document.getElementById('game-heading');
    // game_header.style.display = 'none';

	const dropdown = document.getElementById("dropdown-heading");
    dropdown.style.display = 'none'

	const startGame = document.getElementById("startGame");
    startGame.style.display = 'none'

    fetch('/start_game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, selectedCategory })
    })
    .then(response => response.json())
    .then(data => {
        gameState = data.game_state;
        selectedItems = [];
        tries = 0;

        document.getElementById('name-container').style.display = 'none';
        document.getElementById('game-container').style.display = 'block';
        updateBoard(tries);
        updateLeaderboard();
    });
}
