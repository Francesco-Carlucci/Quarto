import copy

from lib.symmetries import normalize,norm_piece
from lib.RuleBased import check_tris, check_diagonal_tris,check_horizontal_tris,get_pieces
from quarto.objects import Player, Quarto
import numpy as np
import random

hit=0
miss=0

class RLPlayer(Player):
    def __init__(self, quarto: Quarto, alpha: 0.15, random_factor=0.2) -> None:
        super().__init__(quarto)
        self.qtable=[]
        self.piece_state_history = []
        self.position_state_history = []
        self.alpha = alpha
        self.random_factor = random_factor
        self.pieceG = {}        #{(Board, Piece): Value}
        self.positionG = {}     #{(Board, Piece, Position): Value}
        self.nextpiece=None

    #@profile
    def choose_piece(self) -> int:
        #if self.nextpiece is not None:
        #    return self.nextpiece
        maxG = -10e15
        next_move = None
        randomN = np.random.random()
        game = self._Player__quarto
        board = game.get_board_status()
        #board_str = ','.join([str(_) for _ in board.flatten()]) #game.get_board_str()
        normalBoard, normal_str, inverIdx = normalize(game.get_binary_board())
        availablePieces = [p for p in range(16) if p not in board]

        if randomN < self.random_factor:
            # if random number below random factor, choose random action
            next_move = random.choice(availablePieces)
        else:
            # if exploiting, gather all possible actions and choose one with the highest G (reward)
            uncharted = []
            for piece in availablePieces:
                normal_piece=norm_piece(piece,inverIdx)
                new_state = (normal_str, normal_piece)
                global hit
                if new_state not in self.pieceG:
                    uncharted.append(piece)
                    global  miss
                    miss+=1
                elif self.pieceG[new_state] >= maxG:
                    hit+=1
                    #print("piece------------------------------")
                    maxG = self.pieceG[new_state]
                    next_move = piece
                else:
                    #global hit
                    hit += 1
            if next_move is None and len(uncharted) != 0:     #next_move is None and
                next_move = random.choice(uncharted)
        return next_move

    #@profile
    def place_piece(self) -> tuple[int, int]:
        maxG = -10e15
        next_move = None
        next_piece=None
        randomN = np.random.random()
        game = self._Player__quarto
        board = game.get_board_status()
        #board_str=game.get_board_str()
        availablePos = [(x,y) for x in range(4) for y in range(4) if board[y][x]==-1] #Objects.place is inverted!
        #availablePieces = [p for p in range(16) if p not in board and p!=game.get_selected_piece()]

        if randomN < self.random_factor:
            # if random number below random factor, choose random action
            next_move = random.choice(availablePos)
            #next_piece = random.choice(availablePieces)
            #binary_board = game.get_binary_board()
            #binary_board[next_move[1], next_move[0]][:] = game.get_piece_charachteristics(game.get_selected_piece()).binary
            #normalBoard, next_normboard, inverIdx = normalize(binary_board)
            #next_normpiece = norm_piece(next_piece, inverIdx)
        else:
            # if exploiting, gather all possible actions and choose one with the highest G (reward)
            uncharted = []
            for pos in availablePos:
                piece=game.get_selected_piece()
                #for piece in availablePieces:
                x,y=pos
                #board = game.get_board_status()
                board[y][x]=game.get_selected_piece()
                binary_board=game.get_binary_board()
                #binary_board[y,x][:] = game.get_piece_charachteristics(game.get_selected_piece()).binary
                normalBoard, normal_str, inverIdx = normalize(binary_board)
                normal_piece = norm_piece(piece, inverIdx)
                #board_str=','.join([str(_) for _ in board.flatten()])
                new_state = (normal_str,normal_piece)
                global hit
                if new_state not in self.positionG:
                    uncharted.append((pos,normal_str))
                    global miss
                    miss += 1
                elif self.positionG[new_state] >= maxG:

                    hit += 1
                    #print("position------------------------------")
                    maxG = self.positionG[new_state]
                    next_move = pos
                    #next_piece=piece
                    next_normboard=normal_str
                    next_normpiece=normal_piece
                else:

                    hit += 1
            if next_move is None and len(uncharted) != 0:   #next_move is None and
                next_move,next_normboard = random.choice(uncharted)
        #self.nextpiece=next_piece

        #reward = game.get_state_and_reward(1)
        #self.update_position_state_history((next_normboard, next_normpiece), reward)
        return next_move
    
    def update_piece_state_history(self, state, reward):
        self.piece_state_history.append((state, reward))
        
    def update_position_state_history(self, state, reward):
        self.position_state_history.append((state, reward))
    
    def learn(self):
        target = 0

        for prev, reward in reversed(self.piece_state_history):
            if prev not in self.pieceG:
                self.pieceG[prev] = np.random.uniform(low=1.0, high=0.1)
            self.pieceG[prev] = self.pieceG[prev] + self.alpha * (target - self.pieceG[prev])
            target += reward

        self.piece_state_history = []

        target=0
        
        for prev, reward in reversed(self.position_state_history):
            if prev not in self.positionG:
                self.positionG[prev] = np.random.uniform(low=1.0, high=0.1)
            self.positionG[prev] = self.positionG[prev] + self.alpha * (target - self.positionG[prev])
            target += reward

        self.position_state_history = []

        self.random_factor -= 10e-6
        # decrease random factor each episode of play


class RLPlayerRule(RLPlayer):
    def __init__(self, quarto: Quarto, alpha: 0.15, random_factor=0.2) -> None:
        super().__init__(quarto,alpha,random_factor)
        self.pieces = get_pieces()

    def place_piece(self) -> tuple[int, int]:
        game = self._Player__quarto
        x, y = check_tris(game)
        if x != -1 and y != -1:
            return (y,x)
        return super().place_piece()
    def choose_piece(self)->int:
        game = self._Player__quarto
        board = game.get_board_status()
        pieces = self.pieces
        availablePieces = [p for p in range(16) if p not in board]
        for piece in availablePieces:
            if check_horizontal_tris(board, pieces, piece)[0] == -1 \
                    and check_horizontal_tris(board.T, pieces, piece)[0] != -1 \
                    and check_diagonal_tris(board, pieces, piece) != -1:
                return piece
        return super().choose_piece()


class RLGame(Quarto):
    def __init__(self) -> None:
        super().__init__()
        
    def get_state_and_reward(self, playerID):
        reward = -1
        if self.check_winner() == playerID:
            reward = 1
        #elif self.check_winner()==1-playerID:
        #    reward= -2
        else:
            reward = -1
        normalBoard, normal_str, inverIdx = normalize(self._Quarto__binary_board)
        return normal_str,reward,inverIdx

    def get_board_str(self):
        return ','.join([str(_) for _ in self.get_board_status().flatten()])

    def get_binary_board(self):
        return copy.deepcopy(self._Quarto__binary_board)

    def run(self) -> int:
        '''
        Run the game (with output for every move)
        '''
        winner = -1
        while winner < 0 and not self.check_finished():
            # self.print()
            piece_ok = False
            while not piece_ok:
                selected_piece = self._Quarto__players[self._current_player].choose_piece()
                piece_ok = self.select(selected_piece)
                if not piece_ok:
                    print("stuck! curr player: ", self._current_player)
            piece_ok = False
            board, reward,transIdx = self.get_state_and_reward(self._current_player)
            normal_piece = norm_piece(selected_piece,transIdx)
            if isinstance(self._Quarto__players[self._current_player], RLPlayer):
                self._Quarto__players[self._current_player].update_piece_state_history((board, normal_piece), reward)
            else:
                self._Quarto__players[1-self._current_player].update_piece_state_history((board, normal_piece), -reward)
            self._current_player = (self._current_player + 1) % self.MAX_PLAYERS
            # self.print()
            while not piece_ok:
                x,y = self._Quarto__players[self._current_player].place_piece()
                old_board= self.get_board_str()
                piece_ok = self.place(x, y)
                if not piece_ok:
                    print("place stuck! curr player: ", self._current_player)
            board, reward, _ = self.get_state_and_reward(self._current_player)  #returns normalized board
            if isinstance(self._Quarto__players[self._current_player], RLPlayer):
                self._Quarto__players[self._current_player].update_position_state_history(board, reward)   #old_board, self.get_selected_piece(), (x, y)
            else:
                self._Quarto__players[1-self._current_player].update_position_state_history(board, -reward)
            winner = self.check_winner()
        
        return winner