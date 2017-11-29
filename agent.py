from gameobjects import GameObject as GO
from move import Move
from random import choice


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


class Agent:
    board_height = 25
    board_width = 25

    def __init__(self):
        self.board_items = []
        self.direction = None

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
        self.direction = direction
        legal_moves = self.legal_moves()

        positive_moves = {}
        for food in self.board_items[GO.FOOD]:
            current_manhattan = Point.manhattan(self.board_items[GO.SNAKE_HEAD], food)
            for move in legal_moves:
                possible_position = self.next_position(move)
                manhattan_distance = Point.manhattan(possible_position, food)
                if manhattan_distance <= current_manhattan:
                    positive_moves[manhattan_distance] = move
        if positive_moves:
            return positive_moves[min(positive_moves.keys())]
        elif legal_moves:
            return choice(legal_moves)
        else:
            return Move.STRAIGHT

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

    def legal_moves(self):
        return [move for move in list(Move) if self.next_position(move) in self.board_items[GO.EMPTY] + self.board_items[GO.FOOD]]

    def next_position(self, move):
        current_position = self.board_items[GO.SNAKE_HEAD]
        dx, dy = self.direction.get_new_direction(move).get_xy_manipulation()
        return current_position.move(dx, dy)

    def on_die(self):
        pass
