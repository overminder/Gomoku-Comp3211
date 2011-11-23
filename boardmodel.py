
PLAYER_COUNT = 3

class Board(object):
    def __init__(self):
        self.size = 19
        self.space = make_chess_space(19)
        self.hvals = [0] * PLAYER_COUNT
        self.possible_moves = set()

    def __repr__(self):
        return '<board>'

    def pos_is_valid(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def get_at(self, x, y):
        if self.pos_is_valid(x, y):
            return self.space[y][x]
        else:
            return None

    def del_at(self, x, y):
        piece = self.get_at(x, y)
        self.space[y][x] = None
        change_in_hval = 0
        for group in piece.groups:
            change_in_hval += group.remove(piece)
        self.hvals[piece.owner.pid] += change_in_hval

    def put_at(self, x, y, player):
        from pieces import Piece, merge_dual
        piece = Piece(x, y, player)
        self.space[y][x] = piece
        change_in_hval = 0 # accumulate the change in heuristic value.
        for neighbour in self.find_mergeable_neighbours(piece):
            change_in_hval += merge_dual(self, piece, neighbour)
        self.hvals[player.pid] += change_in_hval
        self.add_possible_move(x, y)
        return piece

    def add_possible_move(self, x, y):
        pm = self.possible_moves
        if (x, y) in pm:
            pm.remove((x, y))
        for (nx, ny) in make_neighbours(x, y):
            if self.pos_is_valid(nx, ny) and self.get_at(nx, ny) is None:
                pm.add((nx, ny))

    def iter_possible_moves(self):
        return iter(list(self.possible_moves))

    def find_mergeable_neighbours(self, piece):
        res = []
        for (nx, ny) in make_neighbours(piece.x, piece.y):
            neighbour = self.get_at(nx, ny)
            if neighbour and neighbour.owner is piece.owner:
                res.append(neighbour)
        return res

def make_chess_space(size, fill=None):
    return [[fill] * size for _ in xrange(size)]

def make_neighbours(x, y):
    return [(x + dx, y + dy) for dx in (-1, 0, 1)
                             for dy in (-1, 0, 1)
                             if not (dx == dy == 0)]

