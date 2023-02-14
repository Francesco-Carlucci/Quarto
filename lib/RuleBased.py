import random
import numpy as np

from quarto.objects import Player, Quarto,Piece

# Find a set of three horizontal cells with a common characteristic.
# It is used also for vertical tris by feeding in the transposed board
# and then switching the returned coordinates.
def check_horizontal_tris(board,pieces,piece,lenTris=3) -> tuple[int, int]:
    #lenTris = len(board) - 1
    for i in range(len(board)):
        empty=[j for j in range(len(board)) if board[i][j]==-1]
        high_values = [elem for elem in board[i] if elem >= 0 and pieces[elem].HIGH]
        coloured_values = [elem for elem in board[i] if elem >= 0 and pieces[elem].COLOURED]
        solid_values = [elem for elem in board[i] if elem >= 0 and pieces[elem].SOLID]
        square_values = [elem for elem in board[i] if elem >= 0 and pieces[elem].SQUARE]
        low_values = [elem for elem in board[i] if elem >= 0 and not pieces[elem].HIGH]
        noncolor_values = [elem for elem in board[i] if elem >= 0 and not pieces[elem].COLOURED]
        hollow_values = [elem for elem in board[i] if elem >= 0 and not pieces[elem].SOLID]
        circle_values = [elem for elem in board[i] if elem >= 0 and not pieces[elem].SQUARE]
        if (len(high_values) == lenTris and pieces[piece].HIGH or \
                len(coloured_values) == lenTris and pieces[piece].COLOURED or \
                len(solid_values) == lenTris and pieces[piece].SOLID or \
                len(square_values) == lenTris and pieces[piece].SQUARE or \
                len(low_values) == lenTris and not pieces[piece].HIGH or \
                len(noncolor_values) == lenTris and not pieces[piece].COLOURED or \
                len(hollow_values) == lenTris and not pieces[piece].SOLID or \
                len(circle_values) == lenTris and not pieces[piece].SQUARE)\
                and len(empty)==1:
            return (i, empty[0])
    return -1, -1

# Find tris on the 2 diagonals of the board.
def check_diagonal_tris(board,pieces,piece,lenTris=3):
    high_values = []
    coloured_values = []
    solid_values = []
    square_values = []
    low_values = []
    noncolor_values = []
    hollow_values = []
    circle_values = []

    #lenTris = len(board) - 1
    empty = -1
    for i in range(len(board)):
        if board[i, i] < 0:
            empty=i
            continue
        if pieces[board[i, i]].HIGH:
            high_values.append(board[i, i])
        else:
            low_values.append(board[i, i])
        if pieces[board[i, i]].COLOURED:
            coloured_values.append(board[i, i])
        else:
            noncolor_values.append(board[i, i])
        if pieces[board[i, i]].SOLID:
            solid_values.append(board[i, i])
        else:
            hollow_values.append(board[i, i])
        if pieces[board[i, i]].SQUARE:
            square_values.append(board[i, i])
        else:
            circle_values.append(board[i, i])
    if len(high_values) == lenTris and pieces[piece].HIGH\
            or len(coloured_values) == lenTris and pieces[piece].COLOURED \
            or len(solid_values) == lenTris and pieces[piece].SOLID \
            or len(square_values) == lenTris and pieces[piece].SQUARE \
            or len(low_values) == lenTris and not pieces[piece].HIGH\
            or len(noncolor_values) == lenTris and not pieces[piece].COLOURED\
            or len(hollow_values) == lenTris and not pieces[piece].SOLID \
            or len(circle_values) == lenTris and not pieces[piece].SQUARE\
            and empty!=-1:
        return empty,empty
    high_values = []
    coloured_values = []
    solid_values = []
    square_values = []
    low_values = []
    noncolor_values = []
    hollow_values = []
    circle_values = []
    empty=-1
    for i in range(len(board)):
        if board[i, len(board) - 1 - i] < 0:
            empty=i
            continue
        if pieces[board[i, len(board) - 1 - i]].HIGH:
            high_values.append(board[i, len(board) - 1 - i])
        else:
            low_values.append(board[i, len(board) - 1 - i])
        if pieces[board[i, len(board) - 1 - i]].COLOURED:
            coloured_values.append(
                board[i, len(board) - 1 - i])
        else:
            noncolor_values.append(
                board[i, len(board) - 1 - i])
        if pieces[board[i, len(board) - 1 - i]].SOLID:
            solid_values.append(board[i, len(board) - 1 - i])
        else:
            hollow_values.append(board[i, len(board) - 1 - i])
        if pieces[board[i, len(board) - 1 - i]].SQUARE:
            square_values.append(board[i, len(board) - 1 - i])
        else:
            circle_values.append(board[i, len(board) - 1 - i])
        if len(high_values) == lenTris and pieces[piece].HIGH \
                or len(coloured_values) == lenTris and pieces[piece].COLOURED \
                or len(solid_values) == lenTris and pieces[piece].SOLID \
                or len(square_values) == lenTris and pieces[piece].SQUARE \
                or len(low_values) == lenTris and not pieces[piece].HIGH \
                or len(noncolor_values) == lenTris and not pieces[piece].COLOURED \
                or len(hollow_values) == lenTris and not pieces[piece].SOLID \
                or len(circle_values) == lenTris and not pieces[piece].SQUARE\
                and empty!=-1:
            return empty, len(board)-1-empty
    return -1,-1

def check_tris(game):
    x, y = check_horizontal_tris(game.get_board_status(), get_pieces(), game.get_selected_piece())
    if x >= 0:
        return (x, y)
    # board transposed for vertical
    x, y = check_horizontal_tris(game.get_board_status().T, get_pieces(), game.get_selected_piece())
    if y >= 0:
        return (y, x)
    x, y = check_diagonal_tris(game.get_board_status(), get_pieces(), game.get_selected_piece())
    if x >= 0:
        return (x, y)
    return (-1,-1)

def get_pieces():
    pieces = []
    pieces.append(Piece(False, False, False, False))  # 0
    pieces.append(Piece(False, False, False, True))  # 1
    pieces.append(Piece(False, False, True, False))  # 2
    pieces.append(Piece(False, False, True, True))  # 3
    pieces.append(Piece(False, True, False, False))  # 4
    pieces.append(Piece(False, True, False, True))  # 5
    pieces.append(Piece(False, True, True, False))  # 6
    pieces.append(Piece(False, True, True, True))  # 7
    pieces.append(Piece(True, False, False, False))  # 8
    pieces.append(Piece(True, False, False, True))  # 9
    pieces.append(Piece(True, False, True, False))  # 10
    pieces.append(Piece(True, False, True, True))  # 11
    pieces.append(Piece(True, True, False, False))  # 12
    pieces.append(Piece(True, True, False, True))  # 13
    pieces.append(Piece(True, True, True, False))  # 14
    pieces.append(Piece(True, True, True, True))  # 15
    return pieces


class rulePlayer(Player):

    def __init__(self, quarto: Quarto,random_factor=1.0) -> None:
        super().__init__(quarto)
        self.pieces=get_pieces()
        self.random_factor=random_factor
        print("Final rule based player with random factor: ",self.random_factor)

    def choose_piece(self) -> int:    #move check to a different function and use in minmax
        game = self._Player__quarto
        board = game.get_board_status()
        pieces = self.pieces
        availablePieces = [p for p in range(16) if p not in board]
        for piece in availablePieces:
            if check_horizontal_tris(board, pieces, piece)[0]==-1 \
                and check_horizontal_tris(board.T,pieces,piece)[0]!=-1\
                and check_diagonal_tris(board,pieces,piece)!=-1:
                return piece
        #Player has already lost, just like this life of ours
        if np.random.random()<self.random_factor:
            return random.choice(availablePieces)
        else:
            return availablePieces[0]

    def place_piece(self) -> tuple[int, int]:

        game = self._Player__quarto
        board = game.get_board_status()
        pieces = self.pieces
        x, y = check_horizontal_tris(board, pieces, game.get_selected_piece())
        if x >= 0:
            return int(y), int(x)
        #board transposed for vertical
        x, y = check_horizontal_tris(board.T, pieces, game.get_selected_piece())
        if y >= 0:
            return int(x), int(y)
        x, y = check_diagonal_tris(board, pieces, game.get_selected_piece())
        if x >= 0:
            return int(y), int(x)
        availablePos=[(y,x) for x in range(4) for y in range(4) if board[x][y]==-1]

        if np.random.random()<self.random_factor:
            return random.choice(availablePos)
        return availablePos[0]  #random.choice([(y,x) for x in range(4) for y in range(4) if board[x][y]==-1])