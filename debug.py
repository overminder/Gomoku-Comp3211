import move
import game
import board

class Case(object):
    def __init__(self):
        self.board = board.Board()
        self.m1 = move.Move(1, 0, game.CIRCLE)
        self.m2 = move.Move(2, 0, game.CIRCLE)
        self.m3 = move.Move(3, 0, game.CIRCLE)
        self.m4 = move.Move(4, 0, game.CIRCLE)
        self.m5 = move.Move(5, 0, game.CIRCLE)

    def test_merge1(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        self.board.place_move(self.m5.x, self.m5.y, self.m5.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        m3 = self.board.get_at(self.m3.x, self.m3.y)
        m5 = self.board.get_at(self.m5.x, self.m5.y)
        m3.belongs_to[0].delete_move(m3)
        print m1.belongs_to
        print m3.belongs_to
        print m5.belongs_to

Case().test_merge1()

