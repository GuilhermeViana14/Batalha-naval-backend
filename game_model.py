
import random
import uuid

class Game:
    def __init__(self):
        self.players = []
        self.current_player = 0
        self.boards = [{'board': [[0] * 5 for _ in range(5)], 'ships': []},
                       {'board': [[0] * 5 for _ in range(5)], 'ships': []}]
        self.ships = {
            'submarino': {'size': 1, 'count': 1},
            'barco': {'size': 2, 'count': 1},
            'navio': {'size': 3, 'count': 1},
            'porta_aviao': {'size': 3, 'count': 1}
        }
        self.game_started = False
        self.winner = None

    def add_player(self, player_id=None):
        if len(self.players) >= 2:
            print("Máximo de jogadores atingido")
            return "Máximo de jogadores atingido", None
        
        # Atribui o próximo ID sequencial aos jogadores
        new_player_id = len(self.players)
        self.players.append(new_player_id)
        print(f"Jogador {new_player_id + 1} adicionado com ID: {new_player_id}")
        return f"Jogador {new_player_id + 1} adicionado", new_player_id

    def start_game(self):
        if len(self.players) == 2:
            self.game_started = True
            self.place_ships(0)
            self.place_ships(1)
            self.print_boards()
            return "Jogo iniciado"
        else:
            return "Necessário dois jogadores para iniciar o jogo"

    def is_game_started(self):
        return self.game_started

    def place_ships(self, player_index):
        for ship_name, ship_info in self.ships.items():
            for _ in range(ship_info['count']):
                self.place_ship(player_index, ship_info['size'], ship_name)

    def place_ship(self, player_index, size, ship_name):
        placed = False
        while not placed:
            x = int(input(f"Jogador {player_index + 1}, insira a coordenada X para o {ship_name} ({size} de comprimento): "))
            y = int(input(f"Jogador {player_index + 1}, insira a coordenada Y para o {ship_name} ({size} de comprimento): "))
            orientation = input(f"Jogador {player_index + 1}, insira a orientação para o {ship_name} (horizontal/vertical): ").strip().lower()

            if orientation not in ['horizontal', 'vertical']:
                print("Orientação inválida! Escolha entre 'horizontal' ou 'vertical'.")
                continue

            board = self.boards[player_index]['board']
            if self.can_place_ship(x, y, size, orientation, board):
                for i in range(size):
                    if orientation == 'horizontal':
                        board[x][y + i] = 1
                    else:
                        board[x + i][y] = 1
                self.boards[player_index]['ships'].append((x, y, size, orientation))
                placed = True
            else:
                print(f"Não é possível colocar o {ship_name} nas coordenadas ({x}, {y}) com a orientação {orientation}. Tente novamente.")

    def can_place_ship(self, x, y, size, orientation, board):
        # Verifica se o navio cabe nas coordenadas fornecidas e se o espaço está livre
        for i in range(size):
            if orientation == 'horizontal':
                if y + i >= len(board[0]) or board[x][y + i] != 0:
                    return False
            else:
                if x + i >= len(board) or board[x + i][y] != 0:
                    return False
        return True

    def make_move(self, player_id, x, y):
        # Verifica se o jogo começou
        if not self.is_game_started():
            return {'hit': False, 'message': 'O jogo não começou ainda. Aguarde os jogadores para iniciar o jogo.', 'boards': self.boards}

        # Verifica se já há um vencedor
        if self.winner is not None:
            self.restart_game()  # Reinicia o jogo
            return {'hit': False, 'message': f"O jogo acabou! O vencedor foi o jogador {self.winner + 1} ({self.players[self.winner] if len(self.players) > self.winner else 'Unknown'}). O jogo foi reiniciado.", 'boards': self.boards}

        if len(self.players) < 2:
            self.restart_game()  # Reinicia o jogo
            return {'hit': False, 'message': 'Não há jogadores suficientes para fazer uma jogada. O jogo foi reiniciado.', 'boards': self.boards}

        current_player_id = self.get_current_player()

        # Verifica se é a vez do jogador atual
        if player_id != current_player_id:
            expected_player_index = 0 if self.current_player == 0 else 1
            expected_player_id = self.players[expected_player_index] if len(self.players) > expected_player_index else None
            return {
                'hit': False,
                'message': f'É a vez do jogador {expected_player_index + 1} ({expected_player_id}).' if expected_player_id is not None else 'Jogadores insuficientes para continuar.',
                'boards': self.boards
            }

        opponent_index = 1 if self.current_player == 0 else 0
        opponent_board = self.boards[opponent_index]['board']

        print(f"Jogada do jogador {player_id} nas coordenadas ({x}, {y})")
        print(f"Tabuleiro do oponente antes da jogada: {opponent_board}")

        # Verifica se a jogada acerta ou erra
        if opponent_board[x][y] == 1:
            opponent_board[x][y] = 2  # Marca como atingido
            if self.check_winner(opponent_index):
                self.winner = self.current_player
                self.game_started = False
                self.print_boards()
                return {
                    'hit': True,
                    'message': f'Jogador {self.current_player + 1} ({player_id}) acertou e venceu o jogo!',
                    'winner': self.players[self.current_player] if len(self.players) > self.current_player else 'Unknown',
                    'x': x,
                    'y': y,
                    'boards': self.boards
                }
            result = {
                'hit': True,
                'message': f'Jogador {self.current_player + 1} ({player_id}) acertou!',
                'x': x,
                'y': y,
                'boards': self.boards
            }
        else:
            opponent_board[x][y] = 3  # Marca como erro
            result = {
                'hit': False,
                'message': f'Jogador {self.current_player + 1} ({player_id}) errou!',
                'x': x,
                'y': y,
                'boards': self.boards
            }

        self.switch_player()  # Troca de jogador
        self.print_boards()  # Imprime os tabuleiros após a jogada
        return result  # Retorna o resultado da jogada

    def check_winner(self, opponent_index):
        for row in self.boards[opponent_index]['board']:
            if 1 in row:  # Verifica se ainda há partes dos navios intactas
                return False
        return True

    def switch_player(self):
        self.current_player = 1 if self.current_player == 0 else 0

    def get_current_player(self):
        return self.players[self.current_player]

    def print_boards(self):
        # Exibe o estado dos tabuleiros de cada jogador
        for i, player_board in enumerate(self.boards):
            player_id = self.players[i]
            print(f"\nTabuleiro do Jogador {i + 1} (ID: {player_id}):")
            for row in player_board['board']:
                print(" ".join(str(cell) for cell in row))

    def reset_game(self):
        self.players.clear()  # Limpa os jogadores
        self.current_player = 0  # Reinicia o jogador atual
        self.boards = [{'board': [[0] * 5 for _ in range(5)], 'ships': []},
                       {'board': [[0] * 5 for _ in range(5)], 'ships': []}]  # Limpa os tabuleiros
        self.ships = {
            'submarino': {'size': 1, 'count': 3},
            'barco': {'size': 2, 'count': 1},
            'navio': {'size': 3, 'count': 2},
            'porta_aviao': {'size': 3, 'count': 1}
        }
        self.game_started = False  # O jogo não foi iniciado
        self.winner = None  # Não há vencedor
        print("O jogo foi reiniciado.")

    def remove_player(self, player_id):
        if player_id in self.players:
            self.players.remove(player_id)
            print(f"Jogador {player_id} removido da partida.")
            
            # Reinicia o jogo se algum jogador sair
            self.reset_game()  # Altere restart_game() para reset_game()
            return f"Jogador {player_id} saiu da partida e o jogo foi reiniciado."
        else:
            return f"Jogador {player_id} não está na partida."
