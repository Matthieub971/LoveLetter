from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import request

app = Flask(__name__)
socketio = SocketIO(app)

players = {}          # mapping sid → username
first_player_sid = None
game_started = False

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    global first_player_sid
    username = data['username'].strip()
    sid = request.sid

    # Ajouter le joueur si pas déjà présent
    if sid not in players:
        players[sid] = username
        print(f"{username} rejoint le jeu (SID={sid})")

        # Définir le premier joueur
        if first_player_sid is None:
            first_player_sid = sid

    # Envoyer l'état du jeu à tous
    emit('game_state', {
        'players': [{'username': name, 'hand_count': 0, 'eliminated': False} for name in players.values()],
        'current_turn': None
    }, broadcast=True)

@socketio.on('start_game')
def handle_start_game():
    global game_started
    sid = request.sid
    username = players.get(sid, None)

    if game_started:
        emit('message', {'msg': 'La partie a déjà commencé !'})
        return

    # Vérifier si c'est le premier joueur
    if sid != first_player_sid:
        emit('message', {'msg': 'Seul le premier joueur peut démarrer la partie !'})
        return

    # Démarrer la partie
    game_started = True
    emit('message', {'msg': f'La partie démarre ! Premier joueur : {players[first_player_sid]}'}, broadcast=True)

    # Exemple : initialiser les mains et le tour
    emit('game_state', {
        'players': [{'username': name, 'hand_count': 2, 'eliminated': False} for name in players.values()],
        'current_turn': players[first_player_sid]
    }, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    global first_player_sid
    sid = request.sid
    username = players.pop(sid, None)
    print(f"{username} a quitté le jeu (SID={sid})")

    # Si le premier joueur part, choisir un nouveau
    if sid == first_player_sid and players:
        first_player_sid = next(iter(players))
        print(f"Nouveau premier joueur : {players[first_player_sid]}")
    elif not players:
        first_player_sid = None
        global game_started
        game_started = False

    # Mettre à jour les autres joueurs
    emit('game_state', {
        'players': [{'username': name, 'hand_count': 0, 'eliminated': False} for name in players.values()],
        'current_turn': None
    }, broadcast=True)

@app.route('/game')
def game_page():
    return render_template("game.html")

if __name__ == '__main__':
    socketio.run(app, debug=True)
