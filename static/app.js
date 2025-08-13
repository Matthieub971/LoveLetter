const socket = io();
let username = "";

function joinGame() {
    username = document.getElementById('username').value;
    socket.emit('join', {username});
}

function startGame() {
    socket.emit('start_game');
}

socket.on('hand', (data) => {
    const handDiv = document.getElementById('hand');
    handDiv.innerHTML = '';
    data.hand.forEach(card => {
        const btn = document.createElement('button');
        btn.innerText = card;
        btn.onclick = () => playCard(card);
        handDiv.appendChild(btn);
    });
});

function playCard(card) {
    socket.emit('play_card', {username, card});
}

socket.on('update_state', (state) => {
    console.log("Game state:", state);
});
