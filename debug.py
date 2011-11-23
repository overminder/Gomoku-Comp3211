from boardmodel import Board
from pieces import Piece, PieceGroup, DiagonalUp, merge_dual

board = Board()

class Player(object):
    def __init__(self, pid):
        self.pid = pid
p = Player(0)

add = lambda x, y: board.put_at(x, y, p)
add(2, 2)
assert board.hvals[p.pid] == 0
add(1, 3)
assert board.hvals[p.pid] == 4

