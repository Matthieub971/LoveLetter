import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from game import Game  # <-- notre nouveau module de jeu

app = Flask(__name__)
socketio = SocketIO(app)

# ========================
# Variables globales
# ========================
game = Game()  # Objet unique pour gérer le jeu

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
    sid = str(request.sid)
    username = data.get("username")
    if not username:
        return

    # Ajouter le joueur dans Game
    game.add_player(sid, username)

    # Envoyer la liste des joueurs à tout le monde
    emit('player_list', [p.name for p in game.players], broadcast=True)

    # Dire à ce joueur s'il est hôte (premier joueur)
    emit('is_host', sid == game.players[0].sid, room=sid)

@socketio.on('start_game')
def on_start_game():
    try:
        game.start_game()
    except ValueError as e:
        emit('error', str(e), room=request.sid)
        return

    emit('start_game', broadcast=True)

    current_player = game.get_current_player()

    # Envoyer à chaque joueur sa main privée
    for player in game.players:
        emit('update_hand', player.get_hand(), room=player.sid)
        #emit('is_playing', player.sid == current_player.sid, room=player.sid) 

    emit('update_players', game.get_infos_players(), broadcast=True)
    emit('update_discard_pile', game.get_discard_pile(), broadcast=True)

@socketio.on('play')
def on_play(data):
    """
    data attendu depuis le client : {'cardIndex': int}
    """
    cardIndex = data.get('cardIndex', 0)  # index de la carte à défausser
    current_player = game.get_current_player()

    if current_player:
        # Défausser la carte sélectionnée
        game.handle_turn(current_player.handle_card(cardIndex))
    
    for player in game.players:
        #emit('is_playing', player.sid == game.get_current_player().sid, room=player.sid)
        emit('update_hand', player.get_hand(), room=player.sid)  

    emit('update_players', game.get_infos_players(), broadcast=True) 
    emit('update_discard_pile', game.get_discard_pile(), broadcast=True)


@socketio.on('disconnect')
def on_disconnect():
    sid = str(request.sid)
    player = game.get_player_by_sid(sid)

    if player:
        game.remove_player(sid)

    # Si c'était l'hôte → passer au premier joueur
    if game.players:
        host_sid = game.players[0].sid
        emit('is_host', True, room=host_sid)
    else:
        host_sid = None

    # Ajuster current_turn_index si nécessaire
    if game.current_turn_index >= len(game.players):
        game.current_turn_index = 0

    # Envoyer liste mise à jour
    emit('player_list', [p.name for p in game.players], broadcast=True)

@socketio.on('reset_game')
def on_reset_game():
    game.reset_game()
    emit('player_list', [], broadcast=True)
    emit('game_reset', broadcast=True)

# ========================
# Lancement serveur
# ========================
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
