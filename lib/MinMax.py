import pickle

from quarto.objects import Player, Quarto
from lib.RuleBased import check_tris
from lib.symmetries import normalize, invert_piece, norm_piece
import random
import copy

from line_profiler import LineProfiler
import numpy as np
import os


level_stop=2       #modify, counting number of pos available!
approximation_factor=8

use_symmetries=True

pos_cache=dict()
hit=0
miss=0

def check_horizontal_param(board) -> int:
    hsum=np.nansum(board, axis=1)
    nans=np.sum(np.isnan(board[:,:,0]),axis=1)
    numtre=np.sum(np.logical_and(hsum == 3, (nans == 1).T))
    numzero=np.sum(np.logical_and(hsum == 0, (nans == 1).T))

    return numtre+numzero

def check_diagonal(board):
    #dsum1 = np.trace(board, axis1=1, axis2=2)
    #dsum2 = np.trace(np.fliplr(board), axis1=0, axis2=1)

    diag1=np.diagonal(board, axis1=0, axis2=1).T
    nans1=np.sum(np.isnan(diag1[:,0]))
    dsum1=np.nansum(diag1,axis=0)
    num_tre1=np.sum(dsum1==3)
    numzero1=0
    if nans1==1:
        numzero1= np.sum(dsum1 == 0)

    diag2 = np.diagonal(np.fliplr(board), axis1=0, axis2=1).T
    nans2 = np.sum(np.isnan(diag2[:, 0]))
    dsum2 = np.nansum(diag2, axis=0)
    num_tre2 = np.sum(dsum2 == 3)
    numzero2=0
    if nans2==1:
        numzero2= np.sum(dsum2 == 0)
    return num_tre1+numzero1+num_tre2+numzero2


def heuristic_func(board):
    horiz=check_horizontal_param(board)
    verti=check_horizontal_param(board.T)
    diago=check_diagonal(board)

    return horiz+verti+diago



#@profile
def minmaxplace(game, positions, pieces, lvl, lookforDraw):
    if game.check_winner() >= 0:
        return None,None,-1
    if positions==[]: # or pieces==[]:
        return None,None,0

    x, y = check_tris(game)
    if x != -1 and y != -1:
        return ((x, y), None, 1)

    if lvl>level_stop:   #level stop
        return None,None,heuristic_func(game._Quarto__binary_board)/7
        #positions = random.sample(positions, k=max(int(len(positions)/approximation_factor),1))

        #positions=positions[0:max(int(len(positions)/2),1)]

    bestpos=None
    bestval=-2
    bestnextpiece=None

    for pos in positions:
        """
            New game from previous board
        """
        newGame=Quarto() #.fromBoard(board.get_board_status(),board.get_selected_piece())
        newGame.reset()

        newGame._board=game.get_board_status()
        newGame._Quarto__binary_board=copy.deepcopy(game._Quarto__binary_board)
        """
            Place piece in a position
        """
        newGame.select(game.get_selected_piece())
        newGame.place(pos[1],pos[0])

        if use_symmetries:
            normalBoard,normal_str,inverIdx=normalize(newGame._Quarto__binary_board)
            if normal_str in pos_cache:
                global hit
                hit+=1
                val,nextpiece=pos_cache[normal_str]  #,nextpiece
                invertedpiece=None
                if nextpiece != None:
                    invertedpiece=invert_piece(nextpiece,inverIdx)
                    #inv_perm=np.array([0,1,2,3])
                    #inv_perm[permutations[inverIdx[2]]]=[0,1,2,3]
                    #invertedpiece = binary_pieces[nextpiece][inv_perm]   #np.array(permutations[inverIdx[2]])[permutations[inverIdx[2]]]
                    #invertedpiece = np.logical_xor(invertedpiece, inverIdx[1])
                    #invertedpiece = np.where(np.sum(binary_pieces==invertedpiece,axis=1)==4)[0][0]
                if val==1:
                    return pos,invertedpiece,val  #,nextpiece
                if val>bestval:
                    bestval=val
                    bestpos=pos
                    bestnextpiece=invertedpiece
                continue
            else:
                global miss
                miss+=1

        newPos=copy.deepcopy(positions)
        newPos.remove(pos)
        newPieces=copy.deepcopy(pieces)

        nextpiece, val = minmaxselect(newGame,newPos,newPieces,lvl+1,lookforDraw)

        if val > bestval:
            bestval = val
            bestpos = pos
            bestnextpiece=nextpiece
            if val == 1 or (lookforDraw and val == 0):
                break

        if use_symmetries:
            normal_piece=None
            if nextpiece!=None:
                normal_piece=norm_piece(nextpiece,inverIdx)
                #normal_piece=np.logical_xor(binary_pieces[bestnextpiece], inverIdx[1])
                #normal_piece = normal_piece[permutations[inverIdx[2]]]
                #normal_piece=np.where(np.sum(binary_pieces==normal_piece,axis=1)==4)[0][0]
            pos_cache[normal_str] = val,normal_piece
    return (bestpos,bestnextpiece,bestval)  #if there is no way to win, return best outcome so far

#@profile
def minmaxselect(game, positions, pieces, lvl, lookforDraw):

    if game.check_winner() > 0:
        return None,-1
    if pieces==[]:
        return None,0

    if lvl>level_stop:   #level_stop
        pieces = random.sample(pieces, k=max(int(len(pieces) / approximation_factor), 1))
        #pieces=pieces[0:max(int(len(pieces)/2),1)]
    bestval=2   #look for the min val!
    bestnextpiece=None

    for piece in pieces:
        newGame=Quarto()  #.fromBoard(board.get_board_status(),board.get_selected_piece())
        newGame._board = game.get_board_status()
        newGame._Quarto__binary_board=game._Quarto__binary_board

        newGame.select(piece)
        newPos=copy.deepcopy(positions)
        newPieces=copy.deepcopy(pieces)
        newPieces.remove(piece)

        _,_,val=minmaxplace(newGame,newPos,newPieces,lvl,lookforDraw)

        if val < bestval:
            bestval = val
            bestnextpiece=piece
            if -val == 1 or (lookforDraw and val == 0):
                break

    return bestnextpiece,-bestval
class MinMaxPlayer(Player):

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)
        self.nextpiece = None

        print("stop lvl: ",level_stop," approximation factor: ",approximation_factor)

    def choose_piece(self) -> int:
        if self.nextpiece is not None and self.nextpiece>=0:
            return self.nextpiece
        game = self._Player__quarto
        board = game.get_board_status()
        availablePos = [(x,y) for x in range(4) for y in range(4) if board[x][y]==-1]
        availablePieces=[p for p in range(16) if p not in board]

        lookforDraw = 0
        boardDim = game.BOARD_SIDE ** 2
        if len(availablePos) in [boardDim, boardDim - 1, boardDim - 2, boardDim - 3]:
            lookforDraw = 1

        piece, _ = minmaxselect(game,availablePos,availablePieces,0,lookforDraw)

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

        pos, nextpiece, _ = minmaxplace(game, availablePos, availablePieces,0,lookforDraw)
        self.nextpiece = nextpiece
        x, y = pos

        return y, x
    def save_cache(self):
        global hit
        global miss
        print("hit: ",hit," miss: ",miss," hit ratio: ",hit/(hit+miss))

        with open("./minmaxCache", "bw") as out:
            print("Saving cache to file...")
            pickle.dump(pos_cache, out)

    def read_cache(self):
        if not os.path.exists("./minmaxCache"):
            return
        with open("./minmaxCache","br") as inFile:
            print("Reading cache from file")
            global pos_cache
            pos_cache=pickle.load(inFile)


class MinmaxGame(Quarto):
    def __init__(self)->None:
        super().__init__()

    def get_binary_board(self):
        return copy.deepcopy(self._Quarto__binary_board)

    def run(self) -> int:
        '''
        Run the game (with output for every move)
        '''
        winner = -1
        while winner < 0 and not self.check_finished():

            piece_ok = False
            while not piece_ok:
                piece_ok = self.select(
                    self._Quarto__players[self._current_player].choose_piece())
                if not piece_ok: print("stuck!!!")
            piece_ok = False
            self._current_player = (
                self._current_player + 1) % self.MAX_PLAYERS

            while not piece_ok:
                x, y = self._Quarto__players[self._current_player].place_piece()
                piece_ok = self.place(x, y)
                if not piece_ok: print("stuck!!!")
            winner = self.check_winner()

        return winner

if __name__=="__main__":
    game=MinmaxGame()
    #MinMaxPlayer(game)

    game._Quarto__binary_board=np.array([[[0,0,0,0],[0,0,0,1],[np.nan,np.nan,np.nan,np.nan],[np.nan,np.nan,np.nan,np.nan]],
                                         [[0,1,0,0],[0,1,0,1],[0,1,1,0],[1,0,1,1]],
                                         [[1,0,1,0],[0,0,1,0],[1,0,0,1],[1,1,0,0]],
                                         [[1,1,0,1],[1,1,1,0],
                                [np.nan,np.nan,np.nan,np.nan],[np.nan,np.nan,np.nan,np.nan]]])
    print((game._Quarto__binary_board*np.array([8,4,2,1])).sum(axis=-1)) #.sum(axis=-1)
    game._board=np.array([[0,1,-1,-1],[4,5,6,11],[10,2,9,12],[13,14,-1,-1]])
    game.select(7)

    board = game.get_board_status()
    availablePos = [(x, y) for x in range(4) for y in range(4) if board[x][y] == -1]
    availablePieces = [p for p in range(16) if p not in board.flatten()]

    minmaxplace(game,availablePos,availablePieces,0,0)
    """Profiling minmaxplace!"""

    lp = LineProfiler()
    lp_wrapper = lp(minmaxplace)
    lp_wrapper(game, availablePos, availablePieces, 0, 0)
    lp.print_stats()
    """
    while game.check_winner()<0 and not game.check_finished():
        availablePieces.remove(game.get_selected_piece())
        pos,nextpiece,val=minmaxplace(game,availablePos,availablePieces,0,0)
        print(pos,nextpiece,val)
        game.place(pos[1],pos[0])
        game.print()
        availablePos.remove(pos)
        game.select(nextpiece)
        #piece,val=minmaxselect(game,availablePos,availablePieces,0,0)

    
    pos, nextpiece, val = minmaxplace(game, availablePos, availablePieces, 0, 0)
    game.place(pos[1], pos[0])
    game.print()
    game.select(nextpiece)
    """
