import Quarto
from Player import RandomPlayer,HumanPlayer, minmaxPlayer,rulePlayer
import logging
import argparse

import numpy as np


def main():
    wins = []
    for i in range(100):
        game = Quarto.Quarto()
        game.set_players((RandomPlayer(game),rulePlayer(game)))
        """
        | -1 | 0111 | 0010 | 1001 |
        ---------------------------
        | -1 | 0000 | 0001 | 0011 |
        -------------------
        | -1 | 0100 | 1000 | 1011 |
        -------------------
        | 0110 | 0101 | -1 | 1100 |
        """
        #endgame=np.array([[ -1, 7,2,9 ],[-1,0,1,3],[-1,4,8,11],[6,5,-1,12]])
        #pieces=[p for p in range(15) if p not in [7,2,9,0,1,3,4,8,11,6,5,12]]
        #game.fromBoard(endgame,game.get_selected_piece())
        winner = game.run()
        wins.append(winner)
    logging.warning(f"main: Winner: player {wins}")
    print(sum(wins),"% wins")

    print(f"Winner: player {winner}")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0, help='increase log verbosity')
    parser.add_argument('-d',
                        '--debug',
                        action='store_const',
                        dest='verbose',
                        const=2,
                        help='log debug messages (same as -vv)')
    args = parser.parse_args()

    if args.verbose == 0:
        logging.getLogger().setLevel(level=logging.WARNING)
    elif args.verbose == 1:
        logging.getLogger().setLevel(level=logging.INFO)
    elif args.verbose == 2:
        logging.getLogger().setLevel(level=logging.DEBUG)

    main()