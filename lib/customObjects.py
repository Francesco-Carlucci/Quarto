# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

from quarto.objects import *

class customPiece(Piece):

    piece_to_symbol = {\
        (False, False, False, False): "◃",\
        (False, False, False, True): "⬦",\
        (False, False, True, False): "◂",\
        (False, False, True, True): "⬥",\
        (False, True, False, False): "▵",\
        (False, True, False, True): "▫",\
        (False, True, True, False): "▴",\
        (False, True, True, True): "▪",\
        (True, False, False, False): "◁" ,\
        (True, False, False, True): "◇",\
        (True, False, True, False): "◀" ,\
        (True, False, True, True): "◆",\
        (True, True, False, False): "△",\
        (True, True, False, True): "□",\
        (True, True, True, False): "▲",\
        (True, True, True, True): "⯀",\
    }

    def __init__(self, high: bool, coloured: bool, solid: bool, square: bool) -> None:
        super().__init__(high, coloured, solid, square)
        self.symbol = self.piece_to_symbol[(high, coloured, solid, square)]


class customQuarto(Quarto):

    MAX_PLAYERS = 2
    BOARD_SIDE = 4

    def __init__(self) -> None:
        super.__init__()

    def fromBoard(self,board,selected_piece):
        self.__board=board
        self.__selected_piece_index=selected_piece
        return self

    def print(self):
        '''
        Print the board
        '''
        for row in self.__board:
            print("\n ---------------")
            print("|", end="")
            for element in row:
                #print(f" {element: >2}", end=" |")
                if element == -1:
                    print("  ", end=" |")
                else:
                    print(f" {self.__pieces[element].symbol}", end=" |")

        print("\n ---------------\n")
        print(f"Selected piece: {self.__selected_piece_index}\n")

    def run(self) -> int:
        '''
        Run the game (with output for every move)
        '''
        winner = -1
        while winner < 0 and not self.check_finished():
            self.print()
            piece_ok = False
            while not piece_ok:
                piece_ok = self.select(self.__players[self.__current_player].choose_piece())
            piece_ok = False
            self.__current_player = (self.__current_player + 1) % self.MAX_PLAYERS
            self.print()
            while not piece_ok:
                x, y = self.__players[self.__current_player].place_piece()
                piece_ok = self.place(x, y)
            winner = self.bcheck_winner()
        self.print()
        return winner


class HumanPlayer(Player):

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        pieceIdx = int(input("choose a piece (0-15): "))
        return pieceIdx

    def place_piece(self) -> tuple[int, int]:
        str = input("choose a position (x y): ")
        x, y = str.split(" ")
        return int(x),int(y)
