import copy
from line_profiler import LineProfiler

import numpy as np

permutations=[[0, 1, 2, 3],              [0, 1, 3, 2],              [0, 2, 1, 3],              [0, 2, 3, 1],
              [0, 3, 1, 2],              [0, 3, 2, 1],              [1, 0, 2, 3],              [1, 0, 3, 2],
              [1, 2, 0, 3],              [1, 2, 3, 0],              [1, 3, 0, 2],              [1, 3, 2, 0],
              [2, 0, 1, 3],              [2, 0, 3, 1],              [2, 1, 0, 3],              [2, 1, 3, 0],
              [2, 3, 0, 1],              [2, 3, 1, 0],              [3, 0, 1, 2],              [3, 0, 2, 1],
              [3, 1, 0, 2],              [3, 1, 2, 0],              [3, 2, 0, 1],              [3, 2, 1, 0]]
"""
    Positional transformations (5 basic, 32 combinations) work with matrices shape (n,4,4,4)
"""
def swap_outer(board):
    new_board = np.empty_like(board)
    new_board[:,[0,1,2,3]] = board[:,[1,0,3,2]]         # - swap outer rows    -
    new_board[:,:,[0,1,2,3]]=new_board[:,:,[1,0,3,2]]   # - swap outer columns -
    return new_board
def swap_inner(board):
    new_board = np.empty_like(board)
    new_board[:,[0,1,2,3]] = board[:,[0,2,1,3]]           # - swap inner rows    -
    new_board[:,:,[0,1,2,3]] = new_board[:,:,[0,2,1,3]]   # - swap inner columns -
    return new_board
def swap_3(board):
    return swap_outer(swap_inner(swap_outer(board)))
def transpose(board):
    #return copy.deepcopy(board.T).reshape(board.shape)
    return np.transpose(board,axes=[0,2,1,3])
def rotate(board):
    return copy.deepcopy(np.rot90(board,3,axes=(-3, -2)))
"""
    Apply all positional trasformations to generate 32 boards from the first one
"""
def apply_transformations(board):
    transformations=[swap_outer,swap_inner,swap_3,transpose,rotate]
    boards=board.reshape((1,*board.shape))
    for i in range(5):
        new_boards=transformations[i](boards)
        boards=np.concatenate([boards,new_boards],axis=0)
    return boards
"""
    Create a string with 1 if the board cell is occupied, 0 otherwise
    TODO: compare time with sorted on lists, without str(_) NOT USED ANYMORE
"""
def positional_tag(board):
    old_str=np.array([str(_) for _ in np.where(board.reshape((board.shape[0], -1))>=0,1,0)])
    return old_str
    #np.array([str(_) for _ in np.where(board.reshape((*board.shape[:-2], -1))>=0,1,0)])

#@profile
def normalize(board):
    """
        Apply all 32 positional trasformations
    """
    boards = apply_transformations(board)
    """
        Select board with the highest positional tag
    """
    #tags = positional_tag(boards)
    # candidates = boards[tags == max(tags)]
    np_tags=np.where(boards.reshape((boards.shape[0], -1)) >= 0, 1, 0)  #create positional tags
    candidatesIdx=np.where(np.sum(np_tags==np_tags[np.lexsort(np.rot90(np_tags))[-1]],axis=1)==64)[0] #order candidates based on the tags
    candidates=boards[candidatesIdx]  #select first boards
    """
        Apply xor to the pieces, so the first piece is always 0
        NB: xor preallocated to -1 otherwise empty cells are not preserved
    """
    xored = np.full_like(candidates, np.nan, dtype=np.int32)
    np.logical_xor(candidates, candidates[:, 0, 0].reshape(candidates.shape[0], 1, 1, 4), out=xored,
                   where=np.logical_not(np.isnan(candidates)))
    """
        Apply all 24 bitwise permutations
    """
    permuted = np.array([b[:, :, p] for b in xored for p in permutations])

    #permuted2=[xored[:, :, p] for p in permutations]
    """
        Finds the highest board in lexicographic order, we define it as the normal form TM
    """
    norm_idx=np.lexsort(np.rot90(permuted.reshape(permuted.shape[0],-1)))[0]
    #norm_idx%24=perm_idx    norm_idx//24=candidate_idx   tansf=candidatesIdx[candidate_idx]   xor_value=candidates[candidate_idx, 0, 0]
    candidate_idx=norm_idx // 24
    normal_board = permuted[norm_idx] #min(permuted, key=lambda x: str(x))
    return normal_board, np.array2string(normal_board), (candidatesIdx[candidate_idx],candidates[candidate_idx, 0, 0],norm_idx%24)

binary_pieces=np.array([[0, 0, 0, 0],              [0, 0, 0, 1],            [0, 0, 1, 0],            [0, 0, 1, 1],
                        [0, 1, 0, 0],            [0, 1, 0, 1],            [0, 1, 1, 0],            [0, 1, 1, 1],
                        [1, 0, 0, 0],            [1, 0, 0, 1],            [1, 0, 1, 0],            [1, 0, 1, 1],
                        [1, 1, 0, 0],            [1, 1, 0, 1],            [1, 1, 1, 0],            [1, 1, 1, 1],
                       ])

def invert_piece(piece,transIdx):
    inv_perm = np.array([0, 1, 2, 3])
    inv_perm[permutations[transIdx[2]]] = [0, 1, 2, 3]
    invertedpiece = binary_pieces[piece][inv_perm]  # np.array(permutations[inverIdx[2]])[permutations[inverIdx[2]]]
    invertedpiece = np.logical_xor(invertedpiece, transIdx[1])
    invertedpiece = np.where(np.sum(binary_pieces == invertedpiece, axis=1) == 4)[0][0]

    return invertedpiece
def norm_piece(piece,transIdx):
    normal_piece = np.logical_xor(binary_pieces[piece], transIdx[1])
    normal_piece = normal_piece[permutations[transIdx[2]]]
    normal_piece = np.where(np.sum(binary_pieces == normal_piece, axis=1) == 4)[0][0]
    return normal_piece

def main():
    #board=np.array([[0,1,2,3],[4,5,6,7],[8,9,10,11],[12,13,14,15]])
    board = np.array([[[0,0,0,0],[0,0,0,1], [0,0,1,0], [0,0,1,1]],
                      [[0,1,0,0],[np.nan,np.nan,np.nan,np.nan],[0,1,1,0], [0,1,1,1]],
                      [[1,0,0,0], [1,0,0,1], [1,0,1,0], [1,0,1,1]],
                      [[1,1,0,0], [1,1,0,1], [1,1,1,0],[1,1,1,1]]])
    print("Identita (0):\n",board,'\n')
    print("swap outer (1):\n",swap_outer(board),'\n')
    print("swap inner (2):\n", swap_inner(board), '\n')
    print("swap 3 (3):\n", swap_3(board), '\n')
    print("rotate (4):\n",rotate(board),'\n')
    #print("transpose (5):\n", transpose(board), '\n')

    """
    Apply all 32 positional trasformations
    """
    boards=apply_transformations(board)

    incompletes=np.array([[[-1,1,2,3],[4,5,6,7],[8,9,10,11],[12,13,14,15]]
                         ,[[0,1,2,3],[4,5,-1,7],[8,9,10,11],[12,13,14,15]]
                         , [[3, 1, 2, 0], [4, 5, -1, 7], [8, 10, 9, 11], [12, 13, 14, 15]]
                         ,[[0,1,-1,3],[4,5,6,7],[8,9,-1,11],[12,13,14,15]]
                         ,[[0,1,2,3],[4,5,-1,7],[8,9,10,11],[12,13,1-1,-1]]])
    """
    Select board with the highest positional tag
    """
    tags=positional_tag(boards)
    candidates=boards[tags==max(tags)]
    """
    Apply xor to the pieces, so the first piece is always 0
    """
    xored=np.full_like(candidates,np.nan, dtype=np.int32)
    np.logical_xor(candidates,candidates[:,0,0].reshape(candidates.shape[0],1,1,4),out=xored,where=np.logical_not(np.isnan(candidates)) )
    #print('candidates:','\n',xored) #
    """
    Apply all 24 bitwise permutations
     1   0 1 2 3, 
     2   0 1 3 2,
     3   0 2 1 3,
     4   0 2 3 1,
     5   0 3 1 2,
     6   0 3 2 1,
     7   1 0 2 3,
     8   1 0 3 2,
     9   1 2 0 3,
    10   1 2 3 0,
    11   1 3 0 2,
    12   1 3 2 0,
    13   2 0 1 3,
    14   2 0 3 1,
    15   2 1 0 3,
    16   2 1 3 0,
    17   2 3 0 1,
    18   2 3 1 0,
    19   3 0 1 2,
    20   3 0 2 1,
    21   3 1 0 2,
    22   3 1 2 0,
    23   3 2 0 1,
    24   3 2 1 0,
    """
    permuted=[b[:,:,p] for b in xored for p in permutations]
    sorted_board=sorted(permuted, key=lambda x:str(x))
    normalized,norm_str,_=normalize(board)
    #print("normalized:1\n",sorted_board[0],'\n2\n',normalize(board))
    print(str(normalized),'\n',np.array2string(normalized))

    board2=np.array([[[0,0,0,0],[0,0,0,1],[np.nan,np.nan,np.nan,np.nan],[np.nan,np.nan,np.nan,np.nan]],
                                         [[0,1,0,0],[0,1,0,1],[0,1,1,0],[1,0,1,1]],
                                         [[1,0,1,0],[0,0,1,0],[1,0,0,1],[1,1,0,0]],
                                         [[1,1,0,1],[1,1,1,0],
                                [np.nan,np.nan,np.nan,np.nan],[np.nan,np.nan,np.nan,np.nan]]])
    normal_board,normal_str, inverIdx=normalize(board2)
    #repermuted=normal_board[:,:,np.array(permutations[inverIdx[3]])[permutations[inverIdx[3]]]]
    #rexored=np.logical_xor(repermuted, inverIdx[2])
    lp = LineProfiler()
    lp_wrapper = lp(normalize)
    lp_wrapper(board)
    lp.print_stats()

    print("The End")

if __name__=='__main__':
    main()


