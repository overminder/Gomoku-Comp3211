""" board.py

    Board shall manage more data than we originally expected.
    That is, excessive copying cannot be avoided.

    - 2d-array that maps (x, y) to a chess
    - heurestic value for each player
    - cached possible move for the next player
"""
    
def make_chess_space(size, fill=None):
    loop = xrange(size)
    return [[fill] * size for _ in loop]

def make_neighbours(x, y):
    return [(x + dx, y + dy) for dx in (-1, 0, 1)
                             for dy in (-1, 0, 1)
                             if not (dx == dy == 0)]

def make_larger_neighbours(x, y):
    return [(x + dx, y + dy) for dx in (-2, -1, 0, 1, 2)
                             for dy in (-2, -1, 0, 1, 2)
                             if not (dx == dy == 0)]

class Board(object):
    SIZE = 19
    def __init__(self, space=None):
        from game import PLAYER_COUNT
        self.space = space or make_chess_space(self.SIZE)
        self.heuristic_values = [0] * PLAYER_COUNT
        self.possible_moves = set()

    def __repr__(self):
        from cStringIO import StringIO
        buf = StringIO()
        p = lambda s: buf.write(s)
        nl = lambda: buf.write('\n')

        for y, row in enumerate(self.space):
            p('%2d:' % y)
            for move in row:
                if move is None:
                    p(' ')
                else:
                    p(move.player.mark)
            nl()
        return buf.getvalue()

    def make_deep_copy(self):
        # XXX: design a copy-on-write algorithm on board and groups.
        # Good news is that PyPy is faster than CPython in deepcopy now.
        from copy import deepcopy
        return deepcopy(self)

    def heuristic_value_for(self, player):
        return self.heuristic_values[player.as_id]

    def is_valid_move(self, x, y):
        return 0 <= x < self.SIZE and 0 <= y < self.SIZE

    def get_at(self, x, y):
        assert self.is_valid_move(x, y)
        return self.space[y][x]

    def get_at_safe(self, x, y):
        if not self.is_valid_move(x, y):
            return None
        else:
            return self.space[y][x]

    def del_at(self, x, y):
        move = self.get_at(x, y)
        change_in_hval = 0
        for group in move.belongs_to:
            change_in_hval += group.delete_move(move)
        self.heuristic_values[move.player.as_id] += change_in_hval
        self.space[y][x] = None

    def place_move(self, x, y, player):
        assert self.is_valid_move(x, y)
        self.reconstruct_groups(x, y, player)
        self.add_to_possible_moves(x, y)

    def reconstruct_groups(self, x, y, player):
        """ And re-calculate heuristic value as well.
        """
        from move import Move, merge_dual
        move = Move(x, y, player)
        self.space[y][x] = move
        for neighbour in self.mergeables_of(move):
            # They will always form a new dual.
            change_of_hvalue = merge_dual(self, move, neighbour)
            for group in neighbour.belongs_to:
                # Neighbour may want to merge with new move.
                change_of_hvalue += group.try_merge_move(self, move)
            # XXX: consider the impact on the other two players?
            self.heuristic_values[player.as_id] += change_of_hvalue

    def add_to_possible_moves(self, x, y):
        """ Delete (x, y) while adding valid neighbours.
        """
        if (x, y) in self.possible_moves:
            self.possible_moves.remove((x, y))
        for nx, ny in make_neighbours(x, y):
        #for nx, ny in make_larger_neighbours(x, y):
            if (self.is_valid_move(nx, ny) and self.get_at(nx, ny) is None):
                self.possible_moves.add((nx, ny))

    def iter_possible_moves(self):
        return iter(list(self.possible_moves))

    def mergeables_of(self, move):
        res = []
        for nx, ny in make_neighbours(move.x, move.y):
            if self.is_valid_move(nx, ny):
                # For each valid neighbour
                neighbour = self.get_at(nx, ny)
                if neighbour is None:
                    continue
                if neighbour.player is not move.player:
                    continue
                res.append(neighbour)
        return res


