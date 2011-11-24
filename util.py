
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

BOARD_SIZE = 19

def make_chess_space(size, fill=None):
    return [[fill] * size for _ in xrange(size)]

def make_make_neighbours(width=2):
    code = []
    w = lambda s: code.append(s)
    w('def make_neighbours(x, y):')
    w('    return [')
    range_x = range(width * 2 - 1) # 2 => (0, 1, 2)
    range_y = range(width * 2 - 1) # 3 => (0, 1, 2, 3, 4)
    for dx in range_x:
        dx = dx - width + 1
        for dy in range_y:
            dy = dy - width + 1
            if not dx == dy == 0:
                w('    (x + %d, y + %d),' % (dx, dy))
    w('    ]')
    env = {}
    exec '\n'.join(code) in env
    #print '\n'.join(code)
    return env['make_neighbours']

def make_memorized_neighbours(size):
    table = [[None] * size for _ in xrange(size)]
    make_neighbours = make_make_neighbours(width=2)
    for x in xrange(size):
        for y in xrange(size):
            neighbours = [(nx, ny) for (nx, ny) in make_neighbours(x, y)
                          if 0 <= nx < size and 0 <= ny < size]
            table[y][x] = neighbours
    return table

_memorized_neighbours = make_memorized_neighbours(BOARD_SIZE)
def make_neighbours(x, y):
    return _memorized_neighbours[y][x]


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

