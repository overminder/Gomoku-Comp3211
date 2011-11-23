
class Player(object):
    cache = []
    def __init__(self, name, mark):
        pid = len(self.cache)
        self.pid = pid
        self.cache.append(self)
        self.name = name
        self.mark = mark

    def get_next(self):
        return self.cache[(self.pid + 1) % len(self.cache)]

circle = Player('Circle', 'O')
cross = Player('Cross', 'X')
#square = Player('Square', '=')

PLAYER_COUNT = len(Player.cache)

class Board(object):
    def __init__(self):
        self.size = 19
        self.space = make_chess_space(19)
        # owning piece-groups for each player.
        self.piece_groups = [[0] * 8 for _ in range(PLAYER_COUNT)]
        self.possible_moves = SmallSet(self.size)

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
        for group in piece.groups:
            group.remove(self, piece)

    def put_at(self, x, y, player):
        from pieces import Piece, merge_dual
        piece = Piece(x, y, player)
        self.space[y][x] = piece
        for neighbour in self.find_mergeable_neighbours(piece):
            merge_dual(self, piece, neighbour)
        self.add_possible_move(x, y)
        return piece

    def add_piece_group_(self, pid, length):
        self.piece_groups[pid][length] += 1

    def del_piece_group_(self, pid, length):
        self.piece_groups[pid][length] -= 1

    def get_hval(self, pid):
        from pieces import PieceGroup

        res = 0
        for length, number in enumerate(self.piece_groups[pid]):
            if number:
                res += number * PieceGroup.HVALTAB[length]
        return res

    def add_possible_move(self, x, y):
        pm = self.possible_moves
        pm.del_at(x, y)
        for (nx, ny) in make_neighbours(x, y):
        #for (nx, ny) in make_larger_neighbours(x, y):
            if self.pos_is_valid(nx, ny) and self.get_at(nx, ny) is None:
                pm.put_at(nx, ny)

    def get_possible_moves(self):
        return self.possible_moves

    def set_possible_moves(self, sset):
        self.possible_moves = sset

    def find_mergeable_neighbours(self, piece):
        res = []
        for (nx, ny) in make_neighbours(piece.x, piece.y):
            neighbour = self.get_at(nx, ny)
            if neighbour and neighbour.owner is piece.owner:
                res.append(neighbour)
        return res

# For efficient move recording.
class SmallSet(object):
    def __init__(self, size, data=None):
        self.size = size
        if not data:
            data = [[False] * size for _ in xrange(size)]
        self.data = data

    def put_at(self, x, y):
        self.data[y][x] = True

    def del_at(self, x, y):
        self.data[y][x] = False

    def get_at(self, x, y):
        return self.data[y][x]

    def get_iterator(self):
        return SmallSetIterator(self)

    def make_copy(self):
        # XXX: reduce copy overhead.
        data = [row[:] for row in self.data]
        return SmallSet(self.size, data)

class SmallSetIterator(object):
    def __init__(self, base):
        self.base = base
        self.x = -1
        self.y = 0
        self.peeked = False
        self.closed = False

    def has_next(self):
        if self.closed:
            return False
        if self.peeked:
            return True
        while True:
            self.x += 1
            if self.x >= self.base.size:
                self.x = 0
                self.y += 1
                if self.y >= self.base.size:
                    self.closed = True
                    return False
            value = self.base.get_at(self.x, self.y)
            if value:
                self.peeked = True
                return True
    has_next._always_inline_ = True

    def get_next(self):
        if not self.has_next():
            raise StopIteration
        self.peeked = False
        return (self.x, self.y)
    get_next._always_inline_ = True

def make_chess_space(size, fill=None):
    return [[fill] * size for _ in xrange(size)]

def make_make_neighbours():
    code = []
    w = lambda s: code.append(s)
    w('def make_neighbours(x, y):')
    w('    return [')
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if not dx == dy == 0:
                w('    (x + %d, y + %d),' % (dx, dy))
    w('    ]')
    env = {}
    exec '\n'.join(code) in env
    return env['make_neighbours']

make_neighbours = make_make_neighbours()


