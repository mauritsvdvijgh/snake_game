from gameobjects import GameObject as GO
from move import Move
from sortedcontainers import SortedListWithKey
import copy


class Node:
    def __init__(self, state, snake_head, direction, path_cost, moves=[]):
        self.state = state
        self.snake_head = snake_head
        self.direction = direction
        self.path_cost = path_cost
        self.moves = moves

    def __lt__(self, other):
        return self.path_cost < other.path_cost

    def __eq__(self, other):
        return self.snake_head == other.snake_head

    def __str__(self):
        return "Node(sh=%s, dir=%s, pc=%s" % (self.snake_head, self.direction, self.path_cost)

    def move(self, move):
        direction = self.direction.get_new_direction(move)
        dx, dy = direction.get_xy_manipulation()
        new_snake_head = self.snake_head.move(dx, dy)
        board_copy = self.state[:]
        board_copy[self.snake_head.x][self.snake_head.y] = GO.SNAKE_BODY
        board_copy[new_snake_head.x][new_snake_head.y] = GO.SNAKE_HEAD
        return Node(board_copy, new_snake_head, direction, self.path_cost + 1, self.moves + [move])


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        return Point(self.x + dx, self.y + dy)

    @staticmethod
    def manhattan(p1, p2):
        return abs(p1.x - p2.x) + abs(p1.y - p2.y)

    def __str__(self):
        return "Point(%s,%s)" % (self.x, self.y)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Problem:
    corners = [Point(0, 0), Point(0, 24), Point(24, 0), Point(24, 24)]

    def __init__(self, initial_state, target_location):
        self.initial_state = initial_state
        self.target_location = target_location

    def goal_test(self, node):
        if node.snake_head == self.target_location:
            if self.target_location in Problem.corners:
                return True
            total = 0
            for corner in Problem.corners:
                problem = Problem(Node(node.state, node.snake_head, node.direction, 0), corner)
                path = Agent.a_star_search(problem)
                total = total + 1 if path else total
                if total > 0:
                    return True
        return False

    @staticmethod
    def actions(node):
        for move in list(Move):
            dx, dy = node.direction.get_new_direction(move).get_xy_manipulation()
            new_snake_head = node.snake_head.move(dx, dy)
            if 0 <= new_snake_head.x < 25 and 0 <= new_snake_head.y < 25 and node.state[new_snake_head.x][
                new_snake_head.y] in [GO.FOOD, GO.EMPTY]:
                yield move


class Agent:
    board_height = 25
    board_width = 25

    def __init__(self):
        self.board_items = None
        self.problem = None
        self.path = None
        self.score = None
        self.prev_stall_move = None

    def get_move(self, board, score, turns_alive, turns_to_starve, direction):
        """This function behaves as the 'brain' of the snake. You only need to change the code in this function for
        the project. Every turn the agent needs to return a move. This move will be executed by the snake. If this
        functions fails to return a valid return (see return), the snake will die (as this confuses its tiny brain
        that much that it will explode). The starting direction of the snake will be North.

        :param board: A two dimensional array representing the current state of the board. The upper left most
        coordinate is equal to (0,0) and each coordinate (x,y) can be accessed by executing board[x][y]. At each
        coordinate a GameObject is present. This can be either GameObject.EMPTY (meaning there is nothing at the
        given coordinate), GameObject.FOOD (meaning there is food at the given coordinate), GameObject.WALL (meaning
        there is a wall at the given coordinate. TIP: do not run into them), GameObject.SNAKE_HEAD (meaning the head
        of the snake is located there) and GameObject.SNAKE_BODY (meaning there is a body part of the snake there.
        TIP: also, do not run into these). The snake will also die when it tries to escape the board (moving out of
        the boundaries of the array)

        :param score: The current score as an integer. Whenever the snake eats, the score will be increased by one.
        When the snake tragically dies (i.e. by running its head into a wall) the score will be reset. In ohter
        words, the score describes the score of the current (alive) worm.

        :param turns_alive: The number of turns (as integer) the current snake is alive.

        :param turns_to_starve: The number of turns left alive (as integer) if the snake does not eat. If this number
        reaches 1 and there is not eaten the next turn, the snake dies. If the value is equal to -1, then the option
        is not enabled and the snake can not starve.

        :param direction: The direction the snake is currently facing. This can be either Direction.NORTH,
        Direction.SOUTH, Direction.WEST, Direction.EAST. For instance, when the snake is facing east and a move
        straight is returned, the snake wil move one cell to the right.

        :return: The move of the snake. This can be either Move.LEFT (meaning going left), Move.STRAIGHT (meaning
        going straight ahead) and Move.RIGHT (meaning going right). The moves are made from the viewpoint of the
        snake. This means the snake keeps track of the direction it is facing (North, South, West and East).
        Move.LEFT and Move.RIGHT changes the direction of the snake. In example, if the snake is facing north and the
        move left is made, the snake will go one block to the left and change its direction to west.
        """
        self.board_items = Agent.scan_board(board)
        snake_head_point = self.board_items[GO.SNAKE_HEAD]

        if self.score != score:
            foods = sorted(self.board_items[GO.FOOD], key=lambda x: Point.manhattan(snake_head_point, x))
            for food_point in foods:
                self.problem = Problem(Node(board, snake_head_point, direction, 0), food_point)
                self.path = self.a_star_search(self.problem)
                if self.path:
                    self.score = score
                    self.prev_stall_move = None
                    break

        if self.path:
            return self.path.pop(0)
        else:
            return self.stall(board, direction)

    def stall(self, board, direction):
        snake_head_point = self.board_items[GO.SNAKE_HEAD]
        possible_moves = list(Problem.actions(Node(board, snake_head_point, direction, 0)))
        if self.prev_stall_move:
            move = self.prev_stall_move
            self.prev_stall_move = None
            if move in possible_moves:
                return move
        if Move.STRAIGHT in possible_moves:
            return Move.STRAIGHT
        elif possible_moves:
            self.prev_stall_move = possible_moves[0]
            return possible_moves[0]
        return Move.STRAIGHT

    @staticmethod
    def a_star_search(problem):
        frontier = SortedListWithKey(key=lambda x: x.path_cost + Point.manhattan(x.snake_head, problem.target_location))
        initial_state = copy.deepcopy(problem.initial_state)
        frontier.add(initial_state)
        explored = []
        while True:
            if len(frontier) == 0:
                return False
            node = frontier.pop(0)
            if problem.goal_test(node):
                return node.moves
            explored.append(node)
            for move in problem.actions(node):
                child = node.move(move)
                if child not in explored and child not in frontier:
                    frontier.add(child)
                elif child in frontier:
                    other_node = [n for n in frontier if n == child][0]
                    if child < other_node:
                        frontier.remove(other_node)
                        frontier.add(child)

    def on_die(self):
        self.board_items = None
        self.problem = None
        self.path = None
        self.score = None
        self.prev_stall_move = None

    @staticmethod
    def scan_board(board):
        board_items = {GO.SNAKE_BODY: [], GO.EMPTY: [], GO.WALL: [], GO.FOOD: [], GO.SNAKE_HEAD: None}
        for x in range(Agent.board_width):
            for y in range(Agent.board_height):
                item = board[x][y]
                location = Point(x, y)
                if item == GO.SNAKE_HEAD:
                    board_items[GO.SNAKE_HEAD] = location
                    board_items[GO.SNAKE_BODY].append(location)
                else:
                    board_items[item].append(location)
        return board_items
