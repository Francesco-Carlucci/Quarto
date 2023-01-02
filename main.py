import Quarto
from Player import RandomPlayer,HumanPlayer, minmaxPlayer
import logging
import argparse

import numpy as np


def main():
    game = Quarto.Quarto()
    game.set_players((RandomPlayer(game),minmaxPlayer(game)))
    #endgame=np.array([[9,2,3,-1],[7,-1,6,-1],[-1,11,5,0],[-1,4,-1,8]])
    #pieces=[p for p in range(15) if p not in [9,2,3,0,7,6,11,5,4,8]]
    #game.fromBoard(endgame,pieces,game.get_selected_piece())
    winner = game.run()
    logging.warning(f"main: Winner: player {winner}")

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