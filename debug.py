import move
import game
import board

class Case(object):
    def __init__(self):
        self.board = board.Board()
        self.m1 = move.Move(2, 0, game.CIRCLE)
        self.m2 = move.Move(3, 0, game.CIRCLE)
        self.m3 = move.Move(1, 0, game.CIRCLE)

    def test_merge1(self):
        self.board.space[self.m1.y][self.m1.x] = self.m1
        self.board.space[self.m2.y][self.m2.x] = self.m2
        for neighbour in self.board.mergeables_of(self.m2):
            print 'neigh', neighbour
            move.merge_dual(self.board, self.m2, neighbour)
            neighbour.belongs_to[0].try_merge_move(self.board, self.m2)

        m1 = self.board.get_at(self.m1.x, self.m1.y)
        m2 = self.board.get_at(self.m2.x, self.m2.y)
        print m1.belongs_to
        print m2.belongs_to

        self.board.space[self.m3.y][self.m3.x] = self.m3
        for neighbour in self.board.mergeables_of(self.m3):
            print 'neigh', neighbour
            move.merge_dual(self.board, self.m3, neighbour)
            neighbour.belongs_to[0].try_merge_move(self.board, self.m3)
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        m2 = self.board.get_at(self.m2.x, self.m2.y)
        m3 = self.board.get_at(self.m3.x, self.m3.y)
        print m1.belongs_to
        print m2.belongs_to
        print m3.belongs_to

Case().test_merge1()

