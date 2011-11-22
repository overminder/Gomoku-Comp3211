
import sys
saved_stdout = sys.stdout
sys.stdout = sys.stderr
from unittest import TestCase
import move
import game
import board

class TestThreePlayerGame(TestCase):
    def setUp(self):
        self.board = board.Board()
        self.p1 = game.CIRCLE
        self.p2 = game.CROSS
        self.p3 = game.SQUARE
        self.hvaltab = move.Group.heuristic_table

    def test_some_puts(self):
        self.board.place_move(10, 10, self.p1)
        self.board.place_move(11, 10, self.p2)
        self.board.place_move(9, 10, self.p3)
        self.assertEquals(self.board.heuristic_value_for(self.p1), 0)
        self.assertEquals(self.board.heuristic_value_for(self.p2), 0)
        self.assertEquals(self.board.heuristic_value_for(self.p3), 0)
        self.board.place_move(10, 11, self.p1)
        self.board.place_move(11, 11, self.p2)
        self.board.place_move(9, 11, self.p3)
        self.assertEquals(self.board.heuristic_value_for(self.p1),
                          self.hvaltab[2])
        self.assertEquals(self.board.heuristic_value_for(self.p2),
                          self.hvaltab[2])
        self.assertEquals(self.board.heuristic_value_for(self.p3),
                          self.hvaltab[2])

        board = self.board.make_deep_copy()
        board.place_move(10, 9, self.p1)
        board.place_move(11, 9, self.p2)
        board.place_move(9, 9, self.p3)
        self.assertEquals(board.heuristic_value_for(self.p1),
                          self.hvaltab[3])
        self.assertEquals(board.heuristic_value_for(self.p2),
                          self.hvaltab[3])
        self.assertEquals(board.heuristic_value_for(self.p3),
                          self.hvaltab[3])

        self.assertEquals(self.board.heuristic_value_for(self.p1),
                          self.hvaltab[2])
        self.assertEquals(self.board.heuristic_value_for(self.p2),
                          self.hvaltab[2])
        self.assertEquals(self.board.heuristic_value_for(self.p3),
                          self.hvaltab[2])

class TestMoveInHorizontal(TestCase):
    def setUp(self):
        self.board = board.Board()
        self.m1 = move.Move(1, 0, game.CIRCLE)
        self.m2 = move.Move(2, 0, game.CIRCLE)
        self.m3 = move.Move(3, 0, game.CIRCLE)
        self.m4 = move.Move(4, 0, game.CIRCLE)
        self.m5 = move.Move(5, 0, game.CIRCLE)

    def test_merge_dual(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 2)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[2])

    def test_merge_three1(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 3)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[3])

    def test_merge_three2(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m2.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m3.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 3)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[3])

    def test_merge_four1(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 4)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[4])

    def test_merge_four2(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 4)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[4])

    def test_merge_four3(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 4)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[4])

    def test_merge_five1(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        self.board.place_move(self.m5.x, self.m5.y, self.m5.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 5)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[5])

    def test_merge_five2(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m5.x, self.m5.y, self.m5.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 5)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[5])

    def test_split_five1(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        self.board.place_move(self.m5.x, self.m5.y, self.m5.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        m3 = self.board.get_at(self.m3.x, self.m3.y)
        m5 = self.board.get_at(self.m5.x, self.m5.y)
        self.board.del_at(m3.x, m3.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 2)
        self.assertEquals(len(m5.belongs_to), 1)
        self.assertEquals(len(m5.belongs_to[0]), 2)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[2] * 2)

    def test_deep_copy(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m5.x, self.m5.y, self.m5.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        self.board = self.board.make_deep_copy()
        self.assertEquals(len(list(self.board.iter_possible_moves())),
                          9)
        self.assertIs(self.board.get_at(1, 0).player, game.CIRCLE)

class TestMoveInVertical(TestCase):
    def setUp(self):
        self.board = board.Board()
        self.m1 = move.Move(0, 1, game.CIRCLE)
        self.m2 = move.Move(0, 2, game.CIRCLE)
        self.m3 = move.Move(0, 3, game.CIRCLE)
        self.m4 = move.Move(0, 4, game.CIRCLE)
        self.m5 = move.Move(0, 5, game.CIRCLE)

    def test_merge_dual(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 2)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[2])

    def test_merge_three1(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 3)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[3])

    def test_merge_three2(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m2.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m3.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        m2 = self.board.get_at(self.m2.x, self.m2.y)
        m3 = self.board.get_at(self.m3.x, self.m3.y)
        print m1.belongs_to
        print m2.belongs_to
        print m3.belongs_to
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m2.belongs_to), 1)
        self.assertEquals(len(m3.belongs_to), 1)
        self.assertTrue(isinstance(m1.belongs_to[0], move.Vertical))
        self.assertEquals(len(m1.belongs_to[0]), 3)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[3])

    def test_merge_four1(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 4)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[4])

    def test_merge_four2(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 4)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[4])

    def test_merge_four3(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 4)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[4])

    def test_merge_five1(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        self.board.place_move(self.m5.x, self.m5.y, self.m5.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 5)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[5])

    def test_merge_five2(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m5.x, self.m5.y, self.m5.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 5)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[5])

    def test_split_five1(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        self.board.place_move(self.m5.x, self.m5.y, self.m5.player)
        # Since moves are re-constructed.
        m1 = self.board.get_at(self.m1.x, self.m1.y)
        m3 = self.board.get_at(self.m3.x, self.m3.y)
        m5 = self.board.get_at(self.m5.x, self.m5.y)
        self.board.del_at(m3.x, m3.y)
        self.assertEquals(len(m1.belongs_to), 1)
        self.assertEquals(len(m1.belongs_to[0]), 2)
        self.assertEquals(len(m5.belongs_to), 1)
        self.assertEquals(len(m5.belongs_to[0]), 2)
        self.assertEquals(self.board.heuristic_value_for(game.CIRCLE),
                          move.Group.heuristic_table[2] * 2)

    def test_deep_copy(self):
        self.board.place_move(self.m1.x, self.m1.y, self.m1.player)
        self.board.place_move(self.m3.x, self.m3.y, self.m3.player)
        self.board.place_move(self.m5.x, self.m5.y, self.m5.player)
        self.board.place_move(self.m2.x, self.m2.y, self.m2.player)
        self.board.place_move(self.m4.x, self.m4.y, self.m4.player)
        self.board = self.board.make_deep_copy()
        self.assertEquals(len(list(self.board.iter_possible_moves())),
                          9)
        self.assertIs(self.board.get_at(self.m1.x, self.m1.y).player,
                      game.CIRCLE)

