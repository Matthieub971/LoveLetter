import os
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# ========================
# Variables globales
# ========================
players = []  # liste des pseudos
sid_to_username = {}  # lien entre SID et pseudo
host_sid = None  # SID du joueur hôte

# ========================
# Routes HTTP
# ========================
@app.route('/')
def index():
    return render_template('index.html')

# ========================
# Événements Socket.IO
# ========================
@socketio.on('join')
def on_join(data):
    global host_sid
    username = data['username']
    sid = request.sid

    players[sid] = username

    # Si pas d'hôte défini → premier joueur
    if host_sid is None:
        host_sid = sid

    print(f"{username} a rejoint. Hôte: {players.get(host_sid)}")

    # Mise à jour de la liste pour tous
    for player_sid in players:
        socketio.emit('update_players', {
            'players': list(players.values()),
            'is_host': (player_sid == host_sid)
        }, to=player_sid)

@socketio.on('start_game')
def handle_start():
    sid = request.sid
    if sid == host_sid:
        emit('message', {'msg': 'La partie commence !'}, broadcast=True)
        # Ici on déclenchera plus tard la logique du jeu

@socketio.on('disconnect')
def on_disconnect():
    global host_sid
    sid = request.sid
    username = players.pop(sid, None)

    if username:
        print(f"{username} a quitté.")

    # Si l'hôte est parti → donner rôle au prochain joueur
    if sid == host_sid:
        host_sid = next(iter(players), None)
        if host_sid:
            print(f"Nouvel hôte: {players[host_sid]}")

    # Mise à jour pour tous les joueurs
    for player_sid in players:
        socketio.emit('update_players', {
            'players': list(players.values()),
            'is_host': (player_sid == host_sid)
        }, to=player_sid)

# ========================
# Lancement serveur
# ========================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
