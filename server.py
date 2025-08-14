import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app)

# ========================
# Variables globales
# ========================
# Liste des joueurs connectés : { sid: username }
players = {}
host_sid = None

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
    sid = str(request.sid)
    username = data.get("username")

    if not username:
        return

    # Ajouter le joueur
    players[sid] = username

    # Si pas d'hôte encore, ce joueur devient l'hôte
    if host_sid is None:
        host_sid = sid

    # Envoyer la liste des joueurs à tout le monde
    emit('player_list', list(players.values()), broadcast=True)

    # Dire à ce joueur s'il est hôte
    emit('is_host', sid == host_sid)

@socketio.on('start_game')
def on_start_game():
    # Diffuser à tous que la partie commence
    emit('start_game', broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    global host_sid
    sid = str(request.sid)

    # Retirer le joueur
    players.pop(sid, None)

    # Si c'était l'hôte, passer l'hôte au prochain joueur
    if sid == host_sid:
        host_sid = next(iter(players), None)  # premier joueur restant ou None
        if host_sid:
            # Notifier le nouvel hôte
            emit('is_host', True, room=host_sid)

    # Envoyer la liste mise à jour à tout le monde
    emit('player_list', list(players.values()), broadcast=True)

@socketio.on('reset_game')
def on_reset_game():
    global players, host_sid
    players = {}
    host_sid = None
    emit('player_list', list(players.values()), broadcast=True)
    emit('game_reset', broadcast=True)


# ========================
# Lancement serveur
# ========================
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
