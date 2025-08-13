# server.py
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Page du jeu
@app.route('/')
def index():
    return render_template('index.html')

# Un joueur rejoint
@socketio.on('join')
def handle_join(data):
    username = data['username']
    join_room('salle1')
    emit('message', {'msg': f'{username} a rejoint la partie'}, room='salle1')

# Un joueur joue une carte
@socketio.on('play_card')
def handle_play(data):
    emit('card_played', data, room='salle1')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)