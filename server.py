import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
from game import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Instance unique du jeu
game = Game()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    sid = request.sid

    if game.add_player(sid, username):
        join_room('salle1')
        emit('message', {'msg': f'{username} a rejoint la partie'}, room='salle1')
        emit('game_state', game.get_game_state(), room='salle1')
    else:
        emit('message', {'msg': "La partie a déjà commencé. Impossible de rejoindre."})

@socketio.on('start_game')
def handle_start():
    if game.start():
        emit('message', {'msg': "La partie commence !"}, room='salle1')
        emit('game_state', game.get_game_state(), room='salle1')
    else:
        emit('message', {'msg': "Pas assez de joueurs pour commencer."})

@socketio.on('play_card')
def handle_play(data):
    sid = request.sid
    card_index = data['card_index']

    if game.play_card(sid, card_index):
        emit('game_state', game.get_game_state(), room='salle1')
    else:
        emit('message', {'msg': "Coup invalide."}, to=sid)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
