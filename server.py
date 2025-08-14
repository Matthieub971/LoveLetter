import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# ========================
# Variables globales
# ========================
# { sid: { "username": str, "hand": list[dict] } }
players = {}
host_sid = None
turn_order = []
current_turn_index = 0

# ========================
# Cartes fictives pour test
# ========================
CARD_IMAGES = {
    "Garde": "/static/cartes/Garde.png",
    "Prêtre": "/static/cartes/Pretre.png",
    "Baron": "/static/cartes/Baron.png"
}

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
    players[sid] = {"username": username, "hand": []}
    turn_order.append(sid)

    # Si pas d'hôte encore, ce joueur devient l'hôte
    if host_sid is None:
        host_sid = sid

    # Donner 1 carte de départ
    players[sid]["hand"] = [{"name": "Garde", "image": CARD_IMAGES["Garde"]}]
    emit('update_hand', players[sid]["hand"], room=sid)

    # Envoyer la liste des joueurs à tout le monde
    emit('player_list', [p["username"] for p in players.values()], broadcast=True)

    # Dire à ce joueur s'il est hôte
    emit('is_host', sid == host_sid, room=sid)

@socketio.on('start_game')
def on_start_game():
    global current_turn_index
    current_turn_index = 0
    emit('start_game', broadcast=True)
    if turn_order:
        give_turn(turn_order[current_turn_index])

def give_turn(sid):
    """Donner 2 cartes au joueur actif (rarement 3)"""
    players[sid]["hand"] = [
        {"name": "Garde", "image": CARD_IMAGES["Garde"]},
        {"name": "Prêtre", "image": CARD_IMAGES["Prêtre"]}
    ]
    if players[sid]["username"].lower() == "special":
        players[sid]["hand"].append({"name": "Baron", "image": CARD_IMAGES["Baron"]})

    emit('update_hand', players[sid]["hand"], room=sid)

@socketio.on('end_turn')
def on_end_turn():
    """Fin du tour → on remet le joueur précédent à 1 carte et on donne le tour au suivant"""
    global current_turn_index
    if not turn_order:
        return

    # Joueur précédent
    sid_prev = turn_order[current_turn_index]
    if players[sid_prev]["hand"]:
        players[sid_prev]["hand"] = [players[sid_prev]["hand"][0]]
        emit('update_hand', players[sid_prev]["hand"], room=sid_prev)

    # Joueur suivant
    current_turn_index = (current_turn_index + 1) % len(turn_order)
    sid_next = turn_order[current_turn_index]
    give_turn(sid_next)

@socketio.on('disconnect')
def on_disconnect():
    global host_sid, current_turn_index
    sid = str(request.sid)

    # Retirer le joueur
    if sid in players:
        turn_order.remove(sid)
        players.pop(sid, None)

    # Si c'était l'hôte → passer au prochain
    if sid == host_sid:
        host_sid = next(iter(players), None)
        if host_sid:
            emit('is_host', True, room=host_sid)

    # Ajuster current_turn_index si besoin
    if current_turn_index >= len(turn_order):
        current_turn_index = 0

    # Envoyer liste mise à jour
    emit('player_list', [p["username"] for p in players.values()], broadcast=True)

@socketio.on('reset_game')
def on_reset_game():
    global players, host_sid, turn_order, current_turn_index
    players = {}
    host_sid = None
    turn_order = []
    current_turn_index = 0
    emit('player_list', [], broadcast=True)
    emit('game_reset', broadcast=True)

# ========================
# Lancement serveur
# ========================
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
