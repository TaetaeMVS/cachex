# Class that represents a hexagonal grid board
class Board:
    def __init__(self, size, input=None):
        self.size = size
        self.input = input
        self.hexes = {}
        self.start = None
        self.goal = None
        self.came_from = None
        self.cost_so_far = {}
        self.solution = []
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
                if self.hexes[i, j].value == "Goal" or self.hexes[i, j].value == "Start" or self.hexes[i, j].value == "b" or self.hexes[i, j].value == "r":
                    continue
                else:
                    self.hexes[i, j].value = self.hexes[i, j].heuristic()

    # Function to update board with coordinate values for non goal, start or blocked hexes
    def coords(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.hexes[i, j].value == "Goal" or self.hexes[i, j].value == "Start" or self.hexes[i, j].value == "b" or self.hexes[i, j].value == "r":
                    continue
                else:
                    self.hexes[i, j].value = str(self.hexes[i, j].get_coords()[0]) + ',' + str(self.hexes[i, j].get_coords()[1])

    # Function to implement A* search algorithm - adapted from https://www.redblobgames.com/pathfinding/a-star/introduction.html
    def a_star(self):
        solution = []
        coords = self.start.get_coords()
        solution.append((coords, 0))
        came_from = {}
        cost_so_far = {}
        came_from[coords] = None
        cost_so_far[coords] = 0

        while len(solution) > 0:
            current = solution.pop()
            current_coords = current[0]
            if current_coords == self.goal.get_coords():
                break

            for next in self.hexes[current_coords].get_neighbours():
                next.board = self
                if next.value == "b" or next.value == "r":
                    continue
                new_cost = cost_so_far[current_coords] + self.hexes[current_coords].distance(next)
                if next.get_coords() not in cost_so_far or new_cost < cost_so_far[next.get_coords()]:
                    cost_so_far[next.get_coords()] = new_cost
                    priority = new_cost + next.heuristic()
                    solution.append((next.get_coords(), priority))
                    came_from[next.get_coords()] = current_coords

        self.came_from, self.cost_so_far = came_from, cost_so_far

    # Function to reconstruct path - adapted from https://www.redblobgames.com/pathfinding/a-star/implementation.html
    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        self.solution = path

    def output_solution(self):
        if len(self.cost_so_far) == 0:
            return 0
        print(self.cost_so_far[self.goal.get_coords()])
        for i in range(len(self.solution)):
            print(self.solution[i])

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
    def __eq__(self, hex) -> bool:
        return self.x == hex.x and self.y == hex.y

    # Function to add (shift up and right) to hexagon
    def __add__(self, hex):
        return Hexagon(self.x + hex.x, self.y + hex.y, self.value)
    
    # Function to subtract (shift down and left) from hexagon
    def __sub__(self, hex):
        return Hexagon(self.x - hex.x, self.y - hex.y, self.value)
    
    # Function to test if hexagon is in bounds
    def in_bounds(self, n: int) -> bool:
        return 0 <= self.x < n and 0 <= self.y < n

    # Function to check if hexagon is a neighbour
    def is_neighbour(self, hex) -> bool:
        return abs(self.x - hex.x) + abs(self.y - hex.y) == 1 and hex.in_bounds(self.board.size)
    
    # Function to return coordinates of hexagon as a tuple
    def get_coords(self):
        return self.x, self.y

    # Function to find the distance between two hexagons
    def distance(self, hex) -> int:
        return abs(self.x - hex.x) + abs(self.y - hex.y)

    # Heuristic function to find the distance between self and the goal hexagon
    def heuristic(self) -> int:
        return self.distance(self.board.goal)

    # Function to find neighbours for hexagon
    def get_neighbours(self):
        if self.in_bounds(self.board.size):
            if self.is_neighbour(self + Hexagon(0, 1)):
                self.neighbours.append(self + Hexagon(0, 1))
            if self.is_neighbour(self + Hexagon(1, 0)):
                self.neighbours.append(self + Hexagon(1, 0))
            if self.is_neighbour(self + Hexagon(1, -1)):
                self.neighbours.append(self + Hexagon(1, -1))
            if self.is_neighbour(self + Hexagon(0, -1)):
                self.neighbours.append(self + Hexagon(0, -1))
            if self.is_neighbour(self + Hexagon(-1, 0)):
                self.neighbours.append(self + Hexagon(-1, 0))
            if self.is_neighbour(self + Hexagon(-1, 1)):
                self.neighbours.append(self + Hexagon(-1, 1))
        return self.neighbours