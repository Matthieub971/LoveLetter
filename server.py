import os
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from game import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Instance unique du jeu
game = Game()

# Dictionnaire { sid: username }
connected_players = {}

@app.route('/')
def index():
    return render_template('index.html')

# Nouveau joueur rejoint
@socketio.on('join')
def handle_join(data):
    username = data['username']
    sid = request.sid  # on prend toujours le SID fourni par Socket.IO

    # On l’ajoute à la liste des joueurs connectés
    connected_players[sid] = username

    if game.add_player(sid, username):
        join_room('salle1')
        emit_game_state()
    else:
        emit('message', {'msg': 'Impossible de rejoindre (partie déjà commencée).'}, to=sid)

# Lancer la partie
@socketio.on('start_game')
def handle_start():
    # Seul le premier joueur connecté peut démarrer la partie
    first_sid = next(iter(connected_players)) if connected_players else None
    if request.sid != first_sid:
        emit('message', {'msg': 'Seul le premier joueur connecté peut démarrer la partie.'}, to=request.sid)
        return

    if game.start():
        emit_game_state()
    else:
        emit('message', {'msg': 'Il faut au moins 2 joueurs pour commencer.'}, room='salle1')

# Déconnexion d'un joueur
@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in connected_players:
        username = connected_players.pop(sid)
        game.remove_player(username)
        emit_game_state()

# Fonction utilitaire pour envoyer l'état du jeu à chaque joueur individuellement
def emit_game_state():
    for sid, username in connected_players.items():
        state = game.get_game_state_for(username)
        emit('game_state', state, to=sid)

# Vérifie si la partie est terminée
def check_end_game():
    remaining_players = [p for p in game.players if not p.eliminated]
    if len(remaining_players) <= 1 or len(game.deck) == 0:
        winner = remaining_players[0].username if remaining_players else "Aucun"
        emit('message', {'msg': f'Partie terminée ! Gagnant : {winner}'}, room='salle1')
        game.started = False

@app.route('/game')
def game_page():
    return render_template("game.html")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
