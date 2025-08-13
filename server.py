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
def handle_join(data):
    global host_sid
    username = data['username']
    sid = request.sid

    if sid not in sid_to_username:
        sid_to_username[sid] = username
        players.append(username)

    # Si aucun hôte, le premier joueur devient hôte
    if host_sid is None:
        host_sid = sid

    # Met à jour la liste pour tous
    emit('update_players', {
        'players': players,
        'is_host': (sid == host_sid)
    }, broadcast=True)

@socketio.on('start_game')
def handle_start():
    sid = request.sid
    if sid == host_sid:
        emit('message', {'msg': 'La partie commence !'}, broadcast=True)
        # Ici on déclenchera plus tard la logique du jeu

@socketio.on('disconnect')
def handle_disconnect():
    global host_sid
    sid = request.sid

    if sid in sid_to_username:
        username = sid_to_username.pop(sid)
        if username in players:
            players.remove(username)

        # Si l'hôte part, transfert du rôle
        if sid == host_sid:
            host_sid = next(iter(sid_to_username.keys()), None)

        # Diffusion de la nouvelle liste
        emit('update_players', {
            'players': players,
            'is_host': (request.sid == host_sid)
        }, broadcast=True)

# ========================
# Lancement serveur
# ========================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
