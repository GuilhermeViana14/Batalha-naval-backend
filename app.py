from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from game_model import Game

app = Flask(__name__)
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins='*')

game = Game()

@socketio.on('add_player')
def handle_add_player(data=None):  # Adiciona 'data' como argumento opcional
    message = game.add_player()
    emit('player_added', {'message': message}, broadcast=True)

    # Se o jogo tiver dois jogadores, inicie o jogo
    if len(game.players) == 2:
        game.start_game()
        emit('game_started', {'message': 'O jogo começou!'}, broadcast=True)



@socketio.on('start_game')
def handle_start_game():
    message = game.start_game()
    emit('game_started', {'message': message}, broadcast=True)

@socketio.on('make_move')
def handle_make_move(data):
    player_id = data['player_id']
    x = data['x']
    y = data['y']
    result = game.make_move(player_id, x, y)

    emit('move_result', {
        'message': result['message'],
        'boards': result['boards'],  # Envia os tabuleiros para cada jogador
        'winner': result.get('winner'),
        'hit': result.get('hit'),
        'x': result.get('x'),
        'y': result.get('y'),
        'color': result.get('color')
    }, broadcast=True)

    # Se houver um vencedor, finalize o jogo
    if 'winner' in result:
        emit('game_over', {'winner': result['winner']}, broadcast=True)


@socketio.on('leave_game')
def handle_leave_game(data):
    player_id = data['player_id']
    message = game.remove_player(player_id)
    emit('player_left', {'message': message}, broadcast=True)

    # Notifica que o jogo foi reiniciado caso o jogador tenha saído
    emit('game_reset', {'message': 'O jogo foi reiniciado!'}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app)
