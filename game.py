PLAYER_COUNT = 2

class Player(object):
    cache = [None] * PLAYER_COUNT

    def __init__(self, name, mark, pid):
        self.name = name
        self.mark = mark
        self.pid = pid
        self.cache[pid] = self

    def __deepcopy__(self, memo):
        # Player is shared during copy.
        return self

    @property
    def next_player(self):
        return self.cache[(self.pid + 1) % len(self.cache)]

    @property
    def as_id(self):
        return self.pid


CIRCLE = Player('circle', 'O', 0)
CROSS = Player('cross', 'X', 1)
#SQUARE = Player('square', '=', 2)

