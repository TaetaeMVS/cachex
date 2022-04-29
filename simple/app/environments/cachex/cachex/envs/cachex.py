"""
Game of Hex
"""

from six import StringIO
import sys
import gym
from gym import spaces
import numpy as np
from gym import error
from gym.utils import seeding


from stable_baselines3.common import logger


class Player():
    def __init__(self, id, player_color):
        self.id = id
        self.player_color = player_color
        self.points = 0


def make_random_policy(np_random):
    def random_policy(state):
        possible_moves = HexEnv.get_possible_actions(state)
        # No moves left
        if len(possible_moves) == 0:
            return None
        a = np_random.randint(len(possible_moves))
        return possible_moves[a]
    return random_policy


class HexEnv(gym.Env):
    """
    Hex environment. Play against a fixed opponent.
    """
    RED = 0
    BLUE = 1
    metadata = {"render.modes": ["ansi","human"]}

    def __init__(self, verbose = False, manual = False, board_size = 6):
        
        assert isinstance(board_size, int) and board_size >= 1, 'Invalid board size: {}'.format(board_size)
        self.board_size = board_size
        self.name = 'cachex'
        self.verbose = verbose
        self.manual = manual
        self.opponent_type = 'best'
        self.n_players = 2
        self.current_player_num = 1
        self.np_random = np.random.RandomState()
        self.illegal_move_mode = 'lose'
        self.state = None
        self.to_play = HexEnv.RED
        self.players = [Player(1, HexEnv.RED), Player(2, HexEnv.BLUE)]
        self.done = False
        colormap = {
            'red': HexEnv.RED,
            'blue': HexEnv.BLUE,
        }
      
        observation_type = 'numpy3c'
        assert observation_type in ['numpy3c']
        self.observation_type = observation_type

        if self.observation_type != 'numpy3c':
            raise error.Error('Unsupported observation type: {}'.format(self.observation_type))

        # One action for each board position and resign
        self.action_space = spaces.Discrete(self.board_size ** 2 + 1)
        observation = self.reset()
        self.observation_space = spaces.Box(np.zeros(observation.shape), np.ones(observation.shape))
        self.seed()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        # Update the random policy if needed
        if isinstance(self.opponent_type, str):
            if self.opponent_type == 'random':
                self.opponent_type = make_random_policy(self.np_random)
        else:
            self.opponent_type = self.opponent_type
        return [seed]

    def reset(self, board_size = 6):
        self.board_size = board_size
        self.state = np.zeros((3, self.board_size, self.board_size))
        self.state[2, :, :] = 1.0
        self.to_play = HexEnv.RED
        self.players = [Player(1, HexEnv.RED), Player(2, HexEnv.BLUE)]
        self.done = False
        self.current_player_num = 0
        return self.state

    def step(self, action):
        if self.to_play != self.players[self.current_player_num].player_color:
            return self.state, 0., False, {'state': self.state}
        # If already terminal, then don't do anything
        if self.done:
            return self.state, 0., True, {'state': self.state}

        # if HexEnv.pass_move(self.board_size, action):
        #     pass
        if HexEnv.resign_move(self.board_size, action):
            return self.state, -1, True, {'state': self.state}
        elif not HexEnv.valid_move(self.state, action):
            if self.illegal_move_mode == 'raise':
                print(action)
                print(self.valid_move(self.state, action))
                raise
            elif self.illegal_move_mode == 'lose':
                # Automatic loss on illegal move
                print("illegal move made")
                print(action)
                self.done = True
                return self.state, -1., True, {'state': self.state}
            else:
                raise error.Error('Unsupported illegal move action: {}'.format(self.illegal_move_mode))
        else:
            HexEnv.make_move(self.state, action, self.players[self.current_player_num].player_color)
        reward = HexEnv.game_finished(self.state)
        if self.players[self.current_player_num].player_color == HexEnv.BLUE:
            reward = - reward
        self.done = reward != 0
        if not self.done:
            if self.current_player_num == 0:
                self.to_play = HexEnv.BLUE
                self.current_player_num = 1
            elif self.current_player_num == 1:
                self.current_player_num = 0
                self.to_play = HexEnv.RED
        return self.state, reward, self.done, {'state': self.state}

    # def _reset_opponent(self):
    #     if self.opponent == 'random':
    #         self.opponent_policy = random_policy
    #     else:
    #         raise error.Error('Unrecognized opponent policy {}'.format(self.opponent))

    def render(self, mode='human', close=False):
        if close:
            return
        board = self.state
        outfile = StringIO() if mode == 'ansi' else sys.stdout

        outfile.write(' ' * 5)
        for j in range(board.shape[1]):
            outfile.write(' ' +  str(j + 1) + '  | ')
        outfile.write('\n')
        outfile.write(' ' * 5)
        outfile.write('-' * (board.shape[1] * 6 - 1))
        outfile.write('\n')
        for i in range(board.shape[1]):
            outfile.write(' ' * (2 + i * 3) +  str(i + 1) + '  |')
            for j in range(board.shape[1]):
                if board[2, i, j] == 1:
                    outfile.write('  O  ')
                elif board[0, i, j] == 1:
                    outfile.write('  R  ')
                else:
                    outfile.write('  B  ')
                outfile.write('|')
            outfile.write('\n')
            outfile.write(' ' * (i * 3 + 1))
            outfile.write('-' * (board.shape[1] * 7 - 1))
            outfile.write('\n')

        if mode != 'human':
            return outfile

    # @staticmethod
    # def pass_move(board_size, action):
    #     return action == board_size ** 2

    @staticmethod
    def resign_move(board_size, action):
        return action == board_size ** 2

    @staticmethod
    def valid_move(board, action):
        coords = HexEnv.action_to_coordinate(board, action)
        if board[2, coords[0], coords[1]] == 1:
            return True
        else:
            return False
           
        
    @staticmethod
    def make_move(board, action, player):
        coords = HexEnv.action_to_coordinate(board, action)
        if type(coords[0]) == int:
            board[2, coords[0], coords[1]] = 0
            board[player, coords[0], coords[1]] = 1
        else:
            board[2, coords[0].astype(int), coords[1].astype(int)] = 0
            board[player, coords[0].astype(int), coords[1].astype(int)] = 1

    @staticmethod
    def coordinate_to_action(board, coords):
        return coords[0] * board.shape[-1] + coords[1]

    @staticmethod
    def action_to_coordinate(board, action):
        return action // board.shape[-1], action % board.shape[-1]

    @staticmethod
    def get_possible_actions(board):
        free_x, free_y = np.where(board[2, :, :] == 1)
        return [HexEnv.coordinate_to_action(board, [x, y]) for x, y in zip(free_x, free_y)]

    @property
    def current_player(self):
        return self.players[self.current_player_num]

    @staticmethod
    def game_finished(board):
        # Returns 1 if player 1 wins, -1 if player 2 wins and 0 otherwise
        d = board.shape[1]

        inpath = set()
        newset = set()
        for i in range(d):
            if board[0, 0, i] == 1:
                newset.add(i)

        while len(newset) > 0:
            for i in range(len(newset)):
                v = newset.pop()
                inpath.add(v)
                cx = v // d
                cy = v % d
                # Left
                if cy > 0 and board[0, cx, cy - 1] == 1:
                    v = cx * d + cy - 1
                    if v not in inpath:
                        newset.add(v)
                # Right
                if cy + 1 < d and board[0, cx, cy + 1] == 1:
                    v = cx * d + cy + 1
                    if v not in inpath:
                        newset.add(v)
                # Up
                if cx > 0 and board[0, cx - 1, cy] == 1:
                    v = (cx - 1) * d + cy
                    if v not in inpath:
                        newset.add(v)
                # Down
                if cx + 1 < d and board[0, cx + 1, cy] == 1:
                    if cx + 1 == d - 1:
                        return 1
                    v = (cx + 1) * d + cy
                    if v not in inpath:
                        newset.add(v)
                # Up Right
                if cx > 0 and cy + 1 < d and board[0, cx - 1, cy + 1] == 1:
                    v = (cx - 1) * d + cy + 1
                    if v not in inpath:
                        newset.add(v)
                # Down Left
                if cx + 1 < d and cy > 0 and board[0, cx + 1, cy - 1] == 1:
                    if cx + 1 == d - 1:
                        return 1
                    v = (cx + 1) * d + cy - 1
                    if v not in inpath:
                        newset.add(v)

        inpath.clear()
        newset.clear()
        for i in range(d):
            if board[1, i, 0] == 1:
                newset.add(i)

        while len(newset) > 0:
            for i in range(len(newset)):
                v = newset.pop()
                inpath.add(v)
                cy = v // d
                cx = v % d
                # Left
                if cy > 0 and board[1, cx, cy - 1] == 1:
                    v = (cy - 1) * d + cx
                    if v not in inpath:
                        newset.add(v)
                # Right
                if cy + 1 < d and board[1, cx, cy + 1] == 1:
                    if cy + 1 == d - 1:
                        return -1
                    v = (cy + 1) * d + cx
                    if v not in inpath:
                        newset.add(v)
                # Up
                if cx > 0 and board[1, cx - 1, cy] == 1:
                    v = cy * d + cx - 1
                    if v not in inpath:
                        newset.add(v)
                # Down
                if cx + 1 < d and board[1, cx + 1, cy] == 1:
                    v = cy * d + cx + 1
                    if v not in inpath:
                        newset.add(v)
                # Up Right
                if cx > 0 and cy + 1 < d and board[1, cx - 1, cy + 1] == 1:
                    if cy + 1 == d - 1:
                        return -1
                    v = (cy + 1) * d + cx - 1
                    if v not in inpath:
                        newset.add(v)
                # Left Down
                if cx + 1 < d and cy > 0 and board[1, cx + 1, cy - 1] == 1:
                    v = (cy - 1) * d + cx + 1
                    if v not in inpath:
                        newset.add(v)
        return 0
