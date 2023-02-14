import copy
from typing import Tuple, Any

import numpy as np

import Quarto
import random


class RandomPlayer(Quarto.Player):

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        return random.randint(0, 15)

    def place_piece(self) -> tuple[int, int]:
        return random.randint(0, 3), random.randint(0, 3)

class HumanPlayer(Quarto.Player):

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        pieceIdx = int(input("choose a piece (0-15): "))
        return pieceIdx

    def place_piece(self) -> tuple[int, int]:
        str = input("choose a position (x y): ")
        x, y = str.split(" ")
        return int(x),int(y)

def minmaxplace(board,positions,pieces,lvl,lookforDraw):

    x, y = check_horizontal_tris(board.get_board_status(), board.get_pieces(), board.get_selected_piece())
    if x >= 0:
        return ((x,y),None,1)
    # board transposed for vertical
    x, y = check_horizontal_tris(board.get_board_status().T, board.get_pieces(), board.get_selected_piece())
    if y >= 0:
        return ((y,x),None,1)
    x, y = check_diagonal_tris(board.get_board_status(), board.get_pieces(), board.get_selected_piece())
    if x >= 0:
        return ((x,y),None,1)

    if board.check_winner() >= 0: #not needed if there are less than 3 pieces (we can use lookForDraw)
        return None,None,-1
    #if board.check_finished():   #equal to len(positions)
    #    return None,None,0
    if positions==[] or pieces==[]:
        return None,None,0

    if lvl>2:   #level stop
        positions=random.sample(positions, k=max(int(len(positions)/4),1))
        pieces = random.sample(pieces, k=max(int(len(pieces) / 4), 1))

    for pos in positions:
        #for piece in pieces:
        newBoard=Quarto.Quarto().fromBoard(board.get_board_status(),board.get_selected_piece())
        newBoard.place(pos[0],pos[1])
        #newBoard.select(piece)
        newPos=copy.deepcopy(positions)
        newPos.remove(pos)
        newPieces=copy.deepcopy(pieces)
        #newPieces.remove(piece)

        nextpiece,val=minmaxselect(newBoard,newPos,newPieces,lvl+1,lookforDraw)
        if val==1:
            return (pos,nextpiece,val)
        if lookforDraw and val==0:
            return (pos,nextpiece,val)
    return (pos,nextpiece,val)  #if there is no way to win


def minmaxselect(board,positions,pieces,lvl,lookforDraw): #change board to game!

    """
    #game = self._Player__quarto
    #board = game.get_board_status()
    #pieces = game.get_pieces()
    x, y = check_horizontal_tris(board.get_board_status(), board.get_pieces(), board.get_selected_piece())
    if x >= 0:
        return 1
    #board transposed for vertical
    x, y = check_horizontal_tris(board.get_board_status().T, board.get_pieces(), board.get_selected_piece())
    if y >= 0:
        return 1
    x, y = check_diagonal_tris(board.get_board_status(), board.get_pieces(), board.get_selected_piece())
    if x >= 0:
        return 1
    """

    if board.check_winner() > 0:
        return None,-1
    if board.check_finished():
        return None,0
    if positions==[] or pieces==[]:
        return None,0

    if lvl>2:   #level stop
        positions=random.sample(positions, k=max(int(len(positions)/4),1))
        pieces = random.sample(pieces, k=max(int(len(pieces) / 4), 1))

    #for pos in positions:
    for piece in pieces:
        newBoard=Quarto.Quarto().fromBoard(board.get_board_status(),board.get_selected_piece())
        #newBoard.place(pos[0],pos[1])
        newBoard.select(piece)
        newPos=copy.deepcopy(positions)
        #newPos.remove(pos)
        newPieces=copy.deepcopy(pieces)
        newPieces.remove(piece)

        _,_,val=minmaxplace(newBoard,newPos,newPieces,lvl,lookforDraw)
        if -val==1:
            return piece,-val
        if lookforDraw and val==0:
            return (piece,-val)
    return piece,-val

class minmaxPlayer(Quarto.Player):

    def __init__(self, quarto: Quarto.Quarto) -> None:
        super().__init__(quarto)
        self.nextpiece=-1

    def choose_piece(self) -> int:
        if self.nextpiece is not None and self.nextpiece>=0:
            return self.nextpiece
        game=self._Player__quarto
        board=game.get_board_status()
        availablePos=[(x,y) for x in range(4) for y in range(4) if board[x][y]==-1]
        availablePieces=[p for p in range(16) if p not in board]

        lookforDraw = 0
        boardDim = game.BOARD_SIDE ** 2
        if len(availablePos) in [boardDim, boardDim - 1, boardDim - 2, boardDim - 3]:
            lookforDraw = 1

        piece,_=minmaxselect(game,availablePos,availablePieces,0,lookforDraw)

        return piece

    def place_piece(self) -> tuple[int, int]:
        game = self._Player__quarto
        board = game.get_board_status()
        availablePos = [(x, y) for x in range(4) for y in range(4) if board[x][y] == -1]
        availablePieces = [p for p in range(16) if p not in board.flatten() and p!=game.get_selected_piece()]

        lookforDraw = 0
        boardDim = game.BOARD_SIDE ** 2
        if len(availablePos) in [boardDim, boardDim - 1, boardDim - 2, boardDim - 3]:
            lookforDraw = 1

        pos,nextpiece,_ = minmaxplace(game, availablePos, availablePieces,0,lookforDraw)
        self.nextpiece=nextpiece
        x,y=pos

        return y,x

def check_horizontal_tris(board,pieces,piece) -> tuple[int, int]:
    lenTris = len(board) - 1
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

def check_diagonal_tris(board,pieces,piece):
    high_values = []
    coloured_values = []
    solid_values = []
    square_values = []
    low_values = []
    noncolor_values = []
    hollow_values = []
    circle_values = []

    lenTris = len(board) - 1
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
            or len(low_values) == lenTris and pieces[piece].HIGH\
            or len(noncolor_values) == lenTris and pieces[piece].COLOURED\
            or len(hollow_values) == lenTris and pieces[piece].SOLID \
            or len(circle_values) == lenTris and pieces[piece].SQUARE\
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
                or len(low_values) == lenTris and pieces[piece].HIGH \
                or len(noncolor_values) == lenTris and pieces[piece].COLOURED \
                or len(hollow_values) == lenTris and pieces[piece].SOLID \
                or len(circle_values) == lenTris and pieces[piece].SQUARE\
                and empty!=-1:
            return empty, len(board)-1-empty
    return -1,-1


class rulePlayer(Quarto.Player):

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        game = self._Player__quarto
        board = game.get_board_status()
        pieces = game.get_pieces()
        availablePieces = [p for p in range(16) if p not in board]
        for piece in availablePieces:
            if check_horizontal_tris(board, pieces, piece)[0]==-1 \
                and check_horizontal_tris(board.T,pieces,piece)[0]!=-1\
                and check_diagonal_tris(board,pieces,piece)!=-1:
                return piece
        #Player has already lost
        return random.randint(0, 15)
        #return availablePieces[0]

    def place_piece(self) -> tuple[int, int]:

        game = self._Player__quarto
        board = game.get_board_status()
        pieces = game.get_pieces()
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

        return random.randint(0, 3), random.randint(0, 3)