import os
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from game import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Instance unique du jeu
game = Game()

@app.route('/')
def index():
    return render_template('index.html')

# Nouveau joueur rejoint
@socketio.on('join')
def handle_join(data):
    username = data['username']
    sid = data['sid'] if 'sid' in data else request.sid

    if game.add_player(sid, username):
        join_room('salle1')
        emit('message', {'msg': f'{username} a rejoint la partie'}, room='salle1')
        emit_game_state()
    else:
        emit('message', {'msg': 'Impossible de rejoindre (partie déjà commencée).'}, to=sid)

# Lancer la partie
@socketio.on('start_game')
def handle_start():
    if game.start():
        emit('message', {'msg': 'La partie commence !'}, room='salle1')
        emit_game_state()
    else:
        emit('message', {'msg': 'Il faut au moins 2 joueurs pour commencer.'}, room='salle1')

# Jouer une carte
@socketio.on('play_card')
def handle_play(data):
    sid = request.sid
    card_index = data.get('card_index')

    if game.play_card(sid, card_index):
        check_end_game()
        emit_game_state()
    else:
        emit('message', {'msg': "Ce n'est pas votre tour ou carte invalide."}, to=sid)

# Fonction utilitaire pour envoyer l'état de jeu
def emit_game_state():
    emit('game_state', game.get_game_state(), room='salle1')

# Vérifie si la partie est terminée
def check_end_game():
    remaining_players = [p for p in game.players if not p.eliminated]
    if len(remaining_players) <= 1 or len(game.deck) == 0:
        winner = remaining_players[0].username if remaining_players else "Aucun"
        emit('message', {'msg': f'Partie terminée ! Gagnant : {winner}'}, room='salle1')
        game.started = False

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
