import os
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__, static_folder=".", template_folder=".")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

players = []
game_started = False

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on('join')
def handle_join(data):
    global game_started
    username = data['username']

    # Interdire l'entrée si la partie est déjà lancée
    if game_started:
        emit('player_list', players)  # on renvoie juste la liste
        return

    # Ajouter le joueur s'il n'est pas déjà là
    if username not in players:
        players.append(username)
        print(f"{username} a rejoint la partie.")

    # Envoyer la liste mise à jour à tout le monde
    emit('player_list', players, broadcast=True)

    # Si c'est le premier joueur connecté → il pourra lancer la partie
    if len(players) == 1:
        print(f"{username} est l'hôte.")

@socketio.on('start_game')
def handle_start():
    global game_started
    if not game_started and len(players) >= 2:
        game_started = True
        print("La partie commence !")
        emit('start_game', broadcast=True)
    else:
        emit('message', {'msg': 'Il faut au moins 2 joueurs pour commencer.'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
