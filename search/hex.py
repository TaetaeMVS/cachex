# Class that represents a hexagonal grid board
class Board:
    def __init__(self, size, input=None):
        self.size = size
        self.input = input
        self.hexes = {}
        self.start = None
        self.goal = None
        self.solution = None
        for i in range(size):
            for j in range(size):
                if (i, j) in input:
                    self.hexes[i, j] = Hexagon(i, j, input[i, j])
                    self.hexes[i, j].board = self
                    if input[i, j] == "Start":
                        self.start = self.hexes[i, j]
                    if input[i, j] == "Goal":
                        self.goal = self.hexes[i, j]
                else:
                    self.hexes[i, j] = Hexagon(i, j, str(i) + ',' + str(j))
                    self.hexes[i, j].board = self
          
    # Function to convert board from dict to list of coords for print_board helper function
    def convert(self):
        new_board = {}
        n = self.size
        for i in range(n):
            for j in range(n):
                if self.hexes[i, j].value != [i, j]:
                    new_board[i, j] = self.hexes[i, j].value
        return new_board

    # Function to update board with heuristic values for non goal, start or blocked hexes
    def heuristics(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.hexes[i, j].value == "Goal" or self.hexes[i, j].value == "Start" or self.hexes[i, j].value == "b":
                    continue
                else:
                    self.hexes[i, j].value = self.hexes[i, j].heuristic()

    # Function to update board with coordinate values for non goal, start or blocked hexes
    def coords(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.hexes[i, j].value == "Goal" or self.hexes[i, j].value == "Start" or self.hexes[i, j].value == "b":
                    continue
                else:
                    self.hexes[i, j].value = str(self.hexes[i, j].get_coords()[0]) + ',' + str(self.hexes[i, j].get_coords()[1])

# Class that represents a hexagon
class Hexagon:
    def __init__(self, x, y, value='-'):
        self.x = x
        self.y = y
        self.value = value
        self.neighbours = []
        self.visited = False
        self.parent = None
        self.board = None

    # Function to test equality of two hexagons
    def __eq__(self, Hexagon: object) -> bool:
        return self.x == Hexagon.x and self.y == Hexagon.y

    # Function to add (shift up and right) to hexagon
    def __add__(self, Hexagon: object):
        return Hexagon(self.x + Hexagon.x, self.y + Hexagon.y, self.value)
    
    # Function to subtract (shift down and left) from hexagon
    def __sub__(self, Hexagon: object):
        return Hexagon(self.x - Hexagon.x, self.y - Hexagon.y, self.value)
    
    # Function to test if hexagon is in bounds
    def in_bounds(self, n: int) -> bool:
        return 0 <= self.x < n and 0 <= self.y < n

    # Function to check if hexagon is a neighbour
    def is_neighbour(self, Hexagon: object) -> bool:
        return abs(self.x - Hexagon.x) + abs(self.y - Hexagon.y) == 1
    
    # Function to return coordinates of hexagon as a list
    def get_coords(self):
        return [self.x, self.y]

    # Function to find the distance between two hexagons
    def distance(self, Hexagon: object) -> int:
        return abs(self.x - Hexagon.x) + abs(self.y - Hexagon.y)

    # Heuristic function to find the distance between self and the goal hexagon
    def heuristic(self) -> int:
        return self.distance(self.board.goal)