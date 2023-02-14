import logging
import argparse
import random
import pickle
from lib.customObjects import *
from lib.RL import RLPlayer, RLGame, hit, miss, RLPlayerRule
from lib.MinMax import MinMaxPlayer,MinmaxGame
from lib.RuleBased import rulePlayer
import time
import matplotlib.pyplot as plt


class RandomPlayer(Player):
    """Random player"""

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        return random.randint(0, 15)

    def place_piece(self) -> tuple[int, int]:
        return random.randint(0, 3), random.randint(0, 3)


def main():

    game = MinmaxGame()
    num_partite=100

    rl_rule_player = RLPlayerRule(game, alpha=0.01, random_factor=0)
    rl_player = RLPlayer(game, alpha=0.01, random_factor=0)
    minmax_player=MinMaxPlayer(game)
    #minmax_player.read_cache()    #spostare in init, automaticamente!!
    rule_player=rulePlayer(game,random_factor=1.0)
    """
    with open("./agent", "rb") as out:
        print("Reading RL from file...")
        input=pickle.load(out)
        (robot.pieceG, robot.positionG)=input
    """
    game.set_players((rule_player,rl_rule_player))

    wins = []
    start=time.time()
    for _ in range(100):
        #rl_player.random_factor = 0  # /:/ model.evaluate()
        wins.append(game.run())
        game.reset()
    print(time.time()-start," n. partite: ",num_partite)
    print(wins)
    print(f"main: Winner: player {sum([res for res in wins if res>=0])}%")
    # minmax_player.save_cache()

def train():
    nepochs = 1_000_000
    game = RLGame()
    robot = RLPlayer(game, alpha=0.1, random_factor=0.8)
    rl_rule_player = RLPlayerRule(game, alpha=0.05, random_factor=0.8)
    rule_player=rulePlayer(game, random_factor=0)
    #minmax_player=MinMaxPlayer(game)
    #random_player=RandomPlayer(game)
    game.set_players((rule_player,rl_rule_player))
    """
    with open("./agent", "rb") as out:
        print("Reading RL from file...")
        input=pickle.load(out)
        (robot.pieceG, robot.positionG)=input
    """
    print("rand fact: ", rule_player.random_factor)
    perf=[]
    indices=[]
    for i in range(nepochs):
        game.run()
        rl_rule_player.learn()
        game.reset()
        #--test improvements--
        if i%1000==0:
            print("epoch n.: ", i)
            wins=[]
            for _ in range(100):
                #robot.random_factor = 0  # model.evaluate()
                wins.append(game.run())
                game.reset()
            print(robot.random_factor)
            ratio=sum([res for res in wins if res>=0])
            print(f"main: Winner: player {ratio}%")
            perf.append(ratio)
            indices.append(i)
            if i==50_000:
                rule_player.random_factor=0.1
                print("rand fact: ", rule_player.random_factor)
            if i==100_000:
                rule_player.random_factor=0.2
                print("rand fact: ", rule_player.random_factor)
            if i==200_000:
                rule_player.random_factor=0.3
                print("rand fact: ", rule_player.random_factor)
            if i==300_000:
                rule_player.random_factor=0.5
                print("rand fact: ", rule_player.random_factor)
            if i==600_000:
                rule_player.random_factor=0.6
                print("rand fact: ", rule_player.random_factor)
            if i==800_000:
                rule_player.random_factor=0.8
                print("rand fact: ", rule_player.random_factor)
    plt.semilogy(indices, perf, "b")
    plt.show()
    print("final rand fact: ",rule_player.random_factor)
    #game.set_players((minmax_player, robot))

    for i in range(100):
        game.run()
        robot.learn()
        game.reset()
        #--test improvements--
        if i%1000==0:
            print("epoch n.: ", i)
            wins=[]
            for _ in range(100):
                #robot.random_factor = 0  # model.evaluate()
                wins.append(game.run())
                game.reset()
            print(robot.random_factor)
            print(f"main: Winner: player {sum([res for res in wins if res>=0])}%")
    
    with open("./agent", "bw") as out:
        print("Saving to file...")
        print("hit: ", hit, " miss: ",miss, " hit ratio: ", hit / (hit + miss))
        pickle.dump((robot.pieceG, robot.positionG), out)

    wins = []
    for _ in range(100):
        robot.random_factor=0
        wins.append(game.run())
        game.reset()
    print(f"main: Winner: player {sum(wins)}%")
    logging.warning(f"main: Winner: player {sum([res for res in wins if res>=0])}%")

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

    #main()
    train()