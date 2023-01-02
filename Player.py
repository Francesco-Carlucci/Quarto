import copy

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

def minmaxplace(board,positions,pieces,lvl):

    if board.check_winner() >= 0:
        return None,None,-1
    if board.check_finished():
        return None,None,0
    if positions==[] or pieces==[]:
        return None,None,0

    if lvl>2:   #level stop
        positions=random.sample(positions, k=max(int(len(positions)/5),1))
        pieces = random.sample(pieces, k=max(int(len(pieces) / 5), 1))

    for pos in positions:
        for piece in pieces:
            newBoard=Quarto.Quarto().fromBoard(board.get_board_status(),
                                               board.get_pieces(),board.get_selected_piece())
            newBoard.place(pos[0],pos[1])
            newBoard.select(piece)
            newPos=copy.deepcopy(positions)
            newPos.remove(pos)
            newPieces=copy.deepcopy(pieces)
            newPieces.remove(piece)

            _,_,val=minmaxplace(newBoard,newPos,newPieces,lvl+1)
            if -val==1:
                return (pos,piece,-val)
    return (pos,piece,-val)  #if there is no way to win

"""
def minmaxselect(board,positions,pieces,lvl):

    if board.check_winner() > 0:
        return None,None,-1
    if board.check_finished():
        return None,None,0
    if positions==[]and pieces==[]:
        return None,None,0

    if lvl>1:   #level stop
        positions=random.sample(positions, k=max(int(len(positions)/5),1))
        pieces = random.sample(pieces, k=max(int(len(pieces) / 5), 1))

    #for pos in positions:
    for piece in pieces:
        newBoard=Quarto.Quarto().fromBoard(board.get_board_status(),
                                           board.get_pieces(),board.get_selected_piece())
        #newBoard.place(pos[0],pos[1])
        newBoard.select(piece)
        newPos=copy.deepcopy(positions)
        newPos.remove(pos)
        newPieces=copy.deepcopy(pieces)
        newPieces.remove(piece)

        _,_,val=minmaxplace(newBoard,newPos,newPieces,lvl+1)
        if -val==1:
            return (pos,piece,-val)
    return (pos,piece,-val)
"""

class minmaxPlayer(Quarto.Player):

    def __init__(self, quarto: Quarto.Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        game=self._Player__quarto
        board=game.get_board_status()
        availablePos=[(x,y) for x in range(4) for y in range(4) if board[x][y]==-1]
        availablePieces=[p for p in range(16) if p not in board]

        pos,piece,_=minmaxplace(game,availablePos,availablePieces,0)

        return piece

    def place_piece(self) -> tuple[int, int]:
        game = self._Player__quarto
        board = game.get_board_status()
        availablePos = [(x, y) for x in range(4) for y in range(4) if board[x][y] == -1]
        availablePieces = [p for p in range(16) if p not in board.flatten() and p!=game.get_selected_piece()]

        pos, piece, _ = minmaxplace(game, availablePos, availablePieces,0)

        return pos