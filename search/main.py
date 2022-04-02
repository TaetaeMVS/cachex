"""
COMP30024 Artificial Intelligence, Semester 1, 2022
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
from search.util import print_board, print_coordinate
from search.hex import Hexagon, Board

def main():
    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)

    # TODO:
    # Find and print a solution to the board configuration described
    # by `data`.
    # Why not start by trying to print this configuration out using the
    # `print_board` helper function? (See the `util.py` source code for
    # usage information).
    
    # Start solution
    # Convert board from data into dict with coords as keys and values as values
    board_dict = {}
    for i in data["board"]:
        board_dict[i[1], i[2]] = i[0]

    # Retrieve start and goal coords from data
    start = data["start"]
    goal = data["goal"]
    
    # Add start and goal coords to board_dict
    board_dict[start[0], start[1]] = "Start"
    board_dict[goal[0], goal[1]] = "Goal"
    
    # Put placeholder values in every other hex
    for i in range(data["n"]):
        for j in range(data["n"]):
            if (i, j) not in board_dict:
                board_dict[i, j] = str(i) + ',' + str(j)

    # Convert to a 2D array of Hexagons to represent the game board
    game_board = Board(data["n"], board_dict)
    print(game_board)
    print("Start coords: " + str(game_board.start.get_coords()))
    print("Goal coords: " + str(game_board.goal.get_coords()))
    print(game_board.hexes[4, 2].get_coords())
    game_board.a_star()
    game_board.reconstruct_path(game_board.came_from, game_board.start.get_coords(), game_board.goal.get_coords())
    print(game_board.solution)
    print_board(data["n"], game_board.convert(), "ANSI = True", True)
    # print board


