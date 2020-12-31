# Author: Nishma Shakya
# Assignment #6 - Battleship
# Date due: 2020-12-04
# I pledge that I have completed this assignment without
# collaborating with anyone else, in conformance with the
# NYU School of Engineering Policies and Procedures on
# Academic Misconduct.

import random

### DO NOT EDIT BELOW (with the exception of MAX_MISSES) ###

HIT_CHAR = 'x'
MISS_CHAR = 'o'
BLANK_CHAR = '.'
HORIZONTAL = 'h'
VERTICAL = 'v'
MAX_MISSES = 20
SHIP_SIZES = {
    "carrier": 5,
    "battleship": 4,
    "cruiser": 3,
    "submarine": 3,
    "destroyer": 2
}
NUM_ROWS = 10
NUM_COLS = 10
ROW_IDX = 0
COL_IDX = 1
MIN_ROW_LABEL = 'A'
MAX_ROW_LABEL = 'J'


def get_random_position():
    """Generates a random location on a board of NUM_ROWS x NUM_COLS.

    :return: tuple representing a random position on the board
    """

    row_choice = chr(
        random.choice(
            range(
                ord(MIN_ROW_LABEL),
                ord(MIN_ROW_LABEL) + NUM_ROWS
            )
        )
    )

    col_choice = random.randint(0, NUM_COLS - 1)

    return (row_choice, col_choice)


def play_battleship():
    """Controls flow of Battleship games including display of
    welcome and goodbye messages.

    :return: None
    """

    print("Let's Play Battleship!\n")

    game_over = False

    while not game_over:

        game = Game()
        game.display_board()

        while not game.is_complete():
            pos = game.get_guess()
            result = game.check_guess(pos)
            game.update_game(result, pos)
            game.display_board()

        game_over = end_program()

    print("Goodbye.")


### DO NOT EDIT ABOVE (with the exception of MAX_MISSES) ###


class Ship:

    def __init__(self, name, start_position, orientation):
        """Creates a new ship with the given name, placed at start_position in the
        provided orientation. The number of positions occupied by the ship is determined
        by looking up the name in the SHIP_SIZE dictionary.

        :param name: the name of the ship
        :param start_position: tuple representing the starting position of ship on the board
        :param orientation: the orientation of the ship ('v' - vertical, 'h' - horizontal)
        :return: None
        """
        self.name = name
        self.start = start_position
        self.orientation = orientation
        self.sunk = False

        num_positions = SHIP_SIZES[self.name]
        row = self.start[ROW_IDX]  # A-J
        column = self.start[COL_IDX]  # 0-9

        self.positions = {}
        if self.orientation == VERTICAL:
            self.positions[self.start] = False
            row = chr(ord(row) + 1)
            self.start = (row, column)
            for i in range(num_positions - 1):
                self.positions[self.start] = False
                row = chr(ord(row) + 1)
                self.start = (row, column)
        else:
            self.positions[self.start] = False
            column = column + 1
            self.start = (row, column)
            for i in range(num_positions - 1):
                self.positions[self.start] = False
                column = column + 1
                self.start = (row, column)


class Game:
    ########## DO NOT EDIT #########

    _ship_types = ["carrier", "battleship", "cruiser", "submarine", "destroyer"]

    def display_board(self):
        """ Displays the current state of the board."""

        print()
        print("  " + ' '.join('{}'.format(i) for i in range(len(self.board))))
        for row_label in self.board.keys():
            print('{} '.format(row_label) + ' '.join(self.board[row_label]))
        print()

    ########## DO NOT EDIT #########

    def __init__(self, max_misses=MAX_MISSES):
        """ Creates a new game with max_misses possible missed guesses.
        The board is initialized in this function and ships are randomly
        placed on the board.

        :param max_misses: maximum number of misses allowed before game ends
        """
        self.max_misses = max_misses
        self.ships = []
        self.guesses = []
        self.board = {}
        self.initialize_board()
        self.create_and_place_ships()

    def initialize_board(self):
        """Sets the board to it's initial state with each position occupied by
        a period ('.') string.

        :return: None
        """
        row = MIN_ROW_LABEL
        for i in range(NUM_ROWS):
            self.board[row] = [BLANK_CHAR] * 10
            row = chr(ord(row) + 1)

    def in_bounds(self, start_position, ship_size, orientation):
        """Checks that a ship requiring ship_size positions can be placed at start position.

        :param start_position: tuple representing the starting position of ship on the board
        :param ship_size: number of positions needed to place ship
        :param orientation: the orientation of the ship ('v' - vertical, 'h' - horizontal)
        :return status: True if ship placement inside board boundary, False otherwise
        """
        row = start_position[ROW_IDX]
        column = start_position[COL_IDX]
        if orientation == VERTICAL:
            if column in range(NUM_COLS) and (ord(row) + ship_size) <= ord(MAX_ROW_LABEL):
                return True
            else:
                return False
        else:
            if ord(row) in range(ord(MAX_ROW_LABEL) + 1) and (column + ship_size) <= NUM_COLS:
                return True
            else:
                return False

    def overlaps_ship(self, start_position, ship_size, orientation):
        """Checks for overlap between previously placed ships and a potential new ship
        placement requiring ship_size positions beginning at start_position in the
        given orientation.

        :param start_position: tuple representing the starting position of ship on the board
        :param ship_size: number of positions needed to place ship
        :param orientation: the orientation of the ship ('v' - vertical, 'h' - horizontal)
        :return status: True if ship placement overlaps previously placed ship, False otherwise
        """

        row = start_position[ROW_IDX]
        column = start_position[COL_IDX]

        if orientation == VERTICAL:
            for i in range(ship_size):
                for ship in self.ships:
                    if (chr(ord(row) + i), column) in ship.positions:
                        return True

        elif orientation == HORIZONTAL:
            for i in range(ship_size):
                for ship in self.ships:
                    if (row, column + i) in ship.positions:
                        return True

        return False

    def place_ship(self, start_position, ship_size):
        """Determines if placement is possible for ship requiring ship_size positions placed at
        start_position. Returns the orientation where placement is possible or None if no placement
        in either orientation is possible.

        :param start_position: tuple representing the starting position of ship on the board
        :param ship_size: number of positions needed to place ship
        :return orientation: 'h' if horizontal placement possible, 'v' if vertical placement possible,
            None if no placement possible
        """
        self.start_position = start_position
        self.ship_size = ship_size

        if not self.in_bounds(self.start_position, self.ship_size, HORIZONTAL) or not self.in_bounds(
                self.start_position, self.ship_size, VERTICAL):
            return None

        elif self.in_bounds(self.start_position, self.ship_size, HORIZONTAL) and not self.overlaps_ship(
                self.start_position,
                self.ship_size,
                HORIZONTAL):
            return HORIZONTAL
        elif self.in_bounds(self.start_position, self.ship_size, VERTICAL) and not self.overlaps_ship(
                self.start_position,
                self.ship_size,
                VERTICAL):
            return VERTICAL
        else:
            return None

    def create_and_place_ships(self):
        """Instantiates ship objects with valid board placements.

        :return: None
        """
        # _ship_types is a list that contains the names of the
        # ships in decreasing order of size
        for i in range(len(self._ship_types)):
            start_position = get_random_position()
            name = self._ship_types[i]
            size = SHIP_SIZES[name]
            placement = self.place_ship(start_position, size)

            if placement == HORIZONTAL:
                ship = Ship(name, start_position, HORIZONTAL)
                self.ships.append(ship)  # or append name?
            elif placement == VERTICAL:
                ship = Ship(name, start_position, VERTICAL)
                self.ships.append(ship)  # or append name?
            else:
                while placement is None:
                    start_position = get_random_position()
                    name = self._ship_types[i]
                    size = SHIP_SIZES[name]
                    placement = self.place_ship(start_position, size)
                if placement == HORIZONTAL:
                    ship = Ship(name, start_position, HORIZONTAL)
                    self.ships.append(ship)
                elif placement == VERTICAL:
                    ship = Ship(name, start_position, VERTICAL)
                    self.ships.append(ship)

    def get_guess(self):
        """Prompts the user for a row and column to attack. The
        return value is a board position in (row, column) format

        :return position: a board position as a (row, column) tuple
        """
        row = "Z"
        while ord(row) not in range(ord("A"), ord("J") + 1):
            row = input("Enter a row: ")
        column = 100
        while column not in range(10):
            column = int(input("Enter a column: "))
        position = (row, column)
        return position

    def check_guess(self, position):
        """Checks whether or not position is occupied by a ship. A hit is
        registered when position occupied by a ship and position not hit
        previously. A miss occurs otherwise.

        :param position: a (row,column) tuple guessed by user
        :return: guess_status: True when guess results in hit, False when guess results in miss
        """
        guess_status = False
        hit = True
        for ship in self.ships:
            if position in ship.positions:
                guess_status = True
                ship.positions[position] = True
            for key in ship.positions:
                if not ship.positions[key]:
                    hit = False
            if hit:
                ship.sunk = True
                print("You sunk the {}!".format(ship.name))
        return guess_status

    def update_game(self, guess_status, position):
        """Updates the game by modifying the board with a hit or miss
        symbol based on guess_status of position.

        :param guess_status: True when position is a hit, False otherwise
        :param position:  a (row,column) tuple guessed by user
        :return: None
        """

        row = position[ROW_IDX]
        column = position[COL_IDX]

        value = self.board[row]
        if value[column] == BLANK_CHAR:
            if guess_status:
                # update board to hit
                value[column] = HIT_CHAR
            else:
                # update board and guesses attribute (miss)
                value[column] = MISS_CHAR
                self.guesses.append(position)
        elif not guess_status:
            self.guesses.append(position)

    def is_complete(self):
        """Checks to see if a Battleship game has ended. Returns True when the game is complete
        with a message indicating whether the game ended due to successfully sinking all ships
        or reaching the maximum number of guesses. Returns False when the game is not
        complete.

        :return: True on game completion, False otherwise
        """
        if len(self.guesses) == MAX_MISSES:  # when user reaches max number of guesses
            print("SORRY! NO GUESSES LEFT.")
            return True
        for ship in self.ships:
            if ship.sunk is False:
                return False
        print("YOU WIN!")  # when all ships are sunk
        return True


def end_program():
    """Prompts the user with "Play again (Y/N)?" The question is repeated
    until the user enters a valid response (Y/y/N/n). The function returns
    False if the user enters 'Y' or 'y' and returns True if the user enters
    'N' or 'n'.

    :return response: boolean indicating whether to end the program
    """
    end_game = "x"
    responses = ["Y", "y", "N", "n"]
    while end_game not in responses:
        end_game = input("Play again (Y/N)? ")
    if end_game == "y" or end_game == "Y":
        return False
    else:
        return True


def main():
    """Executes one or more games of Battleship."""

    play_battleship()


if __name__ == "__main__":
    main()
