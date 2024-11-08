from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from game_model import Game
import os

app = Flask(__name__)

CORS(app, origins="*", supports_credentials=True)

# Inicializando o SocketIO
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='gevent')

# Instância do jogo
game = Game()

# Evento de conexão
@socketio.on('connect')
def handle_connect():
    print("Novo cliente conectado")
    emit('connection_status', {'message': 'Conectado com sucesso'})

# Evento de desconexão
@socketio.on('disconnect')
def handle_disconnect():
    print("Cliente desconectado")
    emit('connection_status', {'message': 'Desconectado'})

# Evento para adicionar jogador
@socketio.on('add_player')
def handle_add_player(data=None):
    try:
        message = game.add_player()
        emit('player_added', {'message': message}, broadcast=True)

        # Se o jogo tiver dois jogadores, inicie o jogo
        if len(game.players) == 2:
            game.start_game()
            emit('game_started', {'message': 'O jogo começou!'}, broadcast=True)

    except Exception as e:
        emit('error', {'message': f"Erro ao adicionar jogador: {str(e)}"})

# Evento para iniciar o jogo
@socketio.on('start_game')
def handle_start_game():
    try:
        message = game.start_game()
        emit('game_started', {'message': message}, broadcast=True)
    except Exception as e:
        emit('error', {'message': f"Erro ao iniciar o jogo: {str(e)}"})

# Evento para fazer movimento no jogo
@socketio.on('make_move')
def handle_make_move(data):
    try:
        player_id = data['player_id']
        x = data['x']
        y = data['y']
        result = game.make_move(player_id, x, y)

        emit('move_result', {
            'message': result['message'],
            'boards': result['boards'],
            'winner': result.get('winner'),
            'hit': result.get('hit'),
            'x': result.get('x'),
            'y': result.get('y'),
            'color': result.get('color')
        }, broadcast=True)

        # Se houver um vencedor, finalize o jogo
        if 'winner' in result:
            emit('game_over', {'winner': result['winner']}, broadcast=True)

    except Exception as e:
        emit('error', {'message': f"Erro ao fazer o movimento: {str(e)}"})

# Evento para remover jogador
@socketio.on('leave_game')
def handle_leave_game(data):
    try:
        player_id = data['player_id']
        message = game.remove_player(player_id)
        emit('player_left', {'message': message}, broadcast=True)

        # Notifica que o jogo foi reiniciado caso o jogador tenha saído
        emit('game_reset', {'message': 'O jogo foi reiniciado!'}, broadcast=True)

    except Exception as e:
        emit('error', {'message': f"Erro ao remover jogador: {str(e)}"})

# Rodando o servidor
if __name__ == '__main__':
    # Pega a porta da variável de ambiente do Railway ou usa 5000 como fallback
    port = int(os.environ.get('PORT', 5000))
    
    # Roda o servidor Flask com o SocketIO
    socketio.run(app, host='0.0.0.0', port=port, ping_timeout=60)
