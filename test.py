from unittest import TestCase
from random import shuffle

from boardmodel import Board
from pieces import Piece, PieceGroup, DiagonalUp, merge_dual

class Player(object):
    """ Dummy player class
    """
    def __init__(self, pid):
        self.pid = pid
p1 = Player(0)
p2 = Player(1)
p3 = Player(2)

def len2hval(length):
    return PieceGroup.HVALTAB[length]

class TestPieces(TestCase):
    def setUp(self):
        self.piece1 = Piece(2, 2, 'Circle')
        self.piece2 = Piece(1, 3, 'Circle')
        self.piece3 = Piece(3, 1, 'Circle')
        self.piece_group = DiagonalUp()

    def test_piece_init(self):
        self.assertEquals(self.piece1.x, 2)
        self.assertEquals(self.piece1.y, 2)
        self.assertEquals(self.piece1.owner, 'Circle')
        self.assertEquals(self.piece1.groups, [])

    def test_piece_group_init(self):
        self.assertEquals(self.piece_group.pieces, [])
        self.assertEquals(len(self.piece_group), 0)

    def test_piece_group_add(self):
        self.piece_group.add(self.piece1)
        self.assertEquals(self.piece_group.min_x, 2)
        self.assertEquals(self.piece_group.min_y, 2)
        self.piece_group.add(self.piece2)
        self.assertEquals(self.piece_group.min_x, 1)
        self.assertEquals(self.piece_group.min_y, 2)

    def test_piece_group_subset_of_succ(self):
        self.piece_group.add(self.piece1)
        self.piece_group.add(self.piece2)
        self.piece_group.add(self.piece3)
        pg2 = DiagonalUp()
        pg2.add(self.piece1)
        pg2.add(self.piece2)
        self.assertTrue(self.piece_group.is_superset_of(pg2))

    def test_piece_group_subset_of_fail(self):
        pg1 = self.piece_group
        pg2 = DiagonalUp()
        add = lambda who, x, y: who.add(Piece(x, y, 'Circle'))
        add(pg1, 5, 5)
        add(pg1, 6, 4)
        add(pg1, 7, 3)
        add(pg2, 5, 6)
        add(pg2, 6, 5)
        self.assertFalse(pg1.is_superset_of(pg2))

    def test_piece_group_merge(self):
        # cannot test merge without board? simple.
        this = self
        class FakeBoard(object):
            def get_at(self, x, y):
                for p in (this.piece1, this.piece2, this.piece3): 
                    if p.x == x and p.y == y:
                        return p
        self.piece_group.add(self.piece1)
        self.piece_group.add(self.piece2)
        dhval = self.piece_group.merge(FakeBoard(), self.piece3)
        self.assertEquals(dhval, len2hval(3) - len2hval(2))
        self.assertEquals(len(self.piece_group), 3)
        self.assertEquals(self.piece_group.hval, len2hval(3))

    def test_piece_group_merge_dual(self):
        # cannot test merge without board? simple.
        this = self
        class FakeBoard(object):
            def get_at(self, x, y):
                for p in (this.piece1, this.piece2, this.piece3): 
                    #import sys
                    #sys.stderr.write('%r\n' % ((x, y, p),))
                    if p.x == x and p.y == y:
                        return p
        dhval = merge_dual(FakeBoard(), self.piece2, self.piece1)
        self.assertEquals(len(self.piece1.groups), 1)
        self.assertEquals(len(self.piece1.groups[0]), 3)
        self.assertEquals(dhval, len2hval(3))
        self.assertEquals(self.piece1.groups[0].hval, len2hval(3))

    def test_piece_group_merge_group(self):
        self.piece_group.add(self.piece1)
        self.piece_group.add(self.piece2)
        self.piece_group.add(self.piece3)
        pg2 = DiagonalUp()
        pg2.add(self.piece1)
        pg2.add(self.piece2)
        self.assertEquals(pg2.disband(), -len2hval(2))
        self.assertEquals(len(self.piece1.groups), 1)
        self.assertEquals(len(self.piece2.groups), 1)

    def test_piece_group_remove_3to2(self):
        self.piece_group.add(self.piece1)
        self.piece_group.add(self.piece2)
        self.piece_group.add(self.piece3)

        self.piece_group.remove(self.piece2) # which is in the side
        self.assertEquals(len(self.piece1.groups), 1)
        self.assertEquals(len(self.piece1.groups[0]), 2)
        self.assertEquals(len(self.piece3.groups), 1)
        self.assertEquals(len(self.piece3.groups[0]), 2)

    def test_piece_group_remove_3to11(self):
        self.piece_group.add(self.piece1)
        self.piece_group.add(self.piece2)
        self.piece_group.add(self.piece3)

        self.piece_group.remove(self.piece1) # which is in the middle
        self.assertEquals(len(self.piece2.groups), 0)
        self.assertEquals(len(self.piece3.groups), 0)


class TestBoardModel_WithAddingInDiagonalUp(TestCase):
    def setUp(self):
        self.pts = (
            None, # dummy
            (0, 4),
            (1, 3),
            (2, 2),
            (3, 1),
            (4, 0),
        )
        self.board = Board()

    def del_nth(self, nth):
        x, y = self.pts[nth]
        self.board.del_at(x, y)

    def put_nth(self, nth, p=p1):
        x, y = self.pts[nth]
        self.board.put_at(x, y, p)

    def assert_hval_is(self, val, p=p1):
        self.assertEquals(self.board.hvals[p.pid], val)

    def assert_pt_has_nb_groups(self, nth_pt, length):
        x, y = self.pts[nth_pt]
        self.assertEquals(len(self.board.get_at(x, y).groups), length)

    def assert_pt_group_has_len(self, nth_pt, nth_group, length):
        x, y = self.pts[nth_pt]
        self.assertEquals(len(self.board.get_at(x, y).groups[nth_group]),
                          length)

    def test_put_at_3_1(self):
        self.put_nth(1)
        self.put_nth(2)
        self.assert_hval_is(len2hval(2))
        self.assert_pt_has_nb_groups(1, 1)
        self.assert_pt_has_nb_groups(2, 1)
        self.assert_pt_group_has_len(1, nth_group=0, length=2)
        self.assert_pt_group_has_len(2, nth_group=0, length=2)

        self.put_nth(3)
        self.assert_hval_is(len2hval(3))
        self.assert_pt_has_nb_groups(1, 1)
        self.assert_pt_has_nb_groups(2, 1)
        self.assert_pt_has_nb_groups(3, 1)
        self.assert_pt_group_has_len(1, nth_group=0, length=3)
        self.assert_pt_group_has_len(2, nth_group=0, length=3)
        self.assert_pt_group_has_len(3, nth_group=0, length=3)

    def test_put_at_3_2(self):
        self.put_nth(1)
        self.put_nth(3)
        self.assert_hval_is(len2hval(0))
        self.assert_pt_has_nb_groups(1, length=0)
        self.assert_pt_has_nb_groups(3, length=0)

        self.put_nth(2)
        self.assert_hval_is(len2hval(3))
        self.assert_pt_has_nb_groups(1, length=1)
        self.assert_pt_has_nb_groups(2, length=1)
        self.assert_pt_has_nb_groups(3, length=1)
        self.assert_pt_group_has_len(1, nth_group=0, length=3)
        self.assert_pt_group_has_len(2, nth_group=0, length=3)
        self.assert_pt_group_has_len(3, nth_group=0, length=3)

    def test_put_at_3_3(self):
        self.put_nth(2)
        self.put_nth(1)
        self.assert_hval_is(len2hval(2))
        self.assert_pt_has_nb_groups(1, 1)
        self.assert_pt_has_nb_groups(2, 1)
        self.assert_pt_group_has_len(1, nth_group=0, length=2)
        self.assert_pt_group_has_len(2, nth_group=0, length=2)

        self.put_nth(3)
        self.assert_hval_is(len2hval(3))
        self.assert_pt_has_nb_groups(1, length=1)
        self.assert_pt_has_nb_groups(2, length=1)
        self.assert_pt_has_nb_groups(3, length=1)
        self.assert_pt_group_has_len(1, nth_group=0, length=3)
        self.assert_pt_group_has_len(2, nth_group=0, length=3)
        self.assert_pt_group_has_len(3, nth_group=0, length=3)

    def test_del_at_3_1(self):
        self.put_nth(1)
        self.put_nth(2)
        self.put_nth(3)

        self.del_nth(3) # [1 2 _]
        self.assertFalse(self.board.get_at(*self.pts[3]))
        self.assert_hval_is(len2hval(2))
        self.assert_pt_has_nb_groups(1, 1)
        self.assert_pt_has_nb_groups(2, 1)
        self.assert_pt_group_has_len(1, nth_group=0, length=2)
        self.assert_pt_group_has_len(2, nth_group=0, length=2)

    def test_del_at_3_2(self):
        self.put_nth(1)
        self.put_nth(2)
        self.put_nth(3)

        self.del_nth(2) # [1 _ 3]
        self.assertFalse(self.board.get_at(*self.pts[2]))
        self.assert_hval_is(len2hval(0))
        self.assert_pt_has_nb_groups(1, 0)
        self.assert_pt_has_nb_groups(3, 0)

    def test_put_at_4(self):
        seq = [1, 2, 3, 4]
        for _ in xrange(10):
            self.setUp()
            shuffle(seq)
            for nth_pt in seq:
                self.put_nth(nth_pt)
            self.assert_hval_is(len2hval(4))
            for nth_pt in seq:
                self.assert_pt_has_nb_groups(nth_pt, length=1)
                self.assert_pt_group_has_len(nth_pt, nth_group=0, length=4)

    def test_del_at_4_1(self):
        self.put_nth(1)
        self.put_nth(2)
        self.put_nth(3)
        self.put_nth(4)

        self.del_nth(4) # [1 2 3 _]
        self.assertFalse(self.board.get_at(*self.pts[4]))
        self.assert_hval_is(len2hval(3))
        self.assert_pt_has_nb_groups(1, 1)
        self.assert_pt_has_nb_groups(2, 1)
        self.assert_pt_has_nb_groups(3, 1)
        self.assert_pt_group_has_len(1, nth_group=0, length=3)
        self.assert_pt_group_has_len(2, nth_group=0, length=3)
        self.assert_pt_group_has_len(3, nth_group=0, length=3)

    def test_del_at_4_2(self):
        self.put_nth(1)
        self.put_nth(2)
        self.put_nth(3)
        self.put_nth(4)

        self.del_nth(3) # [1 2 _ 4]
        self.assertFalse(self.board.get_at(*self.pts[3]))
        self.assert_hval_is(len2hval(2))
        self.assert_pt_has_nb_groups(1, 1)
        self.assert_pt_has_nb_groups(2, 1)
        self.assert_pt_has_nb_groups(4, 0)
        self.assert_pt_group_has_len(1, nth_group=0, length=2)
        self.assert_pt_group_has_len(2, nth_group=0, length=2)

    def test_put_at_5(self):
        seq = [1, 2, 3, 4, 5]
        for _ in xrange(10):
            self.setUp()
            shuffle(seq)
            for nth_pt in seq:
                self.put_nth(nth_pt)
            self.assert_hval_is(len2hval(5))
            for nth_pt in seq:
                self.assert_pt_has_nb_groups(nth_pt, length=1)
                self.assert_pt_group_has_len(nth_pt, nth_group=0, length=5)

    def test_del_at_5_1(self):
        self.put_nth(1)
        self.put_nth(2)
        self.put_nth(3)
        self.put_nth(4)
        self.put_nth(5)

        self.del_nth(5) # [1 2 3 4 _]
        self.assertFalse(self.board.get_at(*self.pts[5]))
        self.assert_hval_is(len2hval(4))
        self.assert_pt_has_nb_groups(1, 1)
        self.assert_pt_has_nb_groups(2, 1)
        self.assert_pt_has_nb_groups(3, 1)
        self.assert_pt_has_nb_groups(4, 1)
        self.assert_pt_group_has_len(1, nth_group=0, length=4)
        self.assert_pt_group_has_len(2, nth_group=0, length=4)
        self.assert_pt_group_has_len(3, nth_group=0, length=4)
        self.assert_pt_group_has_len(4, nth_group=0, length=4)

    def test_del_at_5_2(self):
        self.put_nth(1)
        self.put_nth(2)
        self.put_nth(3)
        self.put_nth(4)
        self.put_nth(5)

        self.del_nth(4) # [1 2 3 _ 5]
        self.assertFalse(self.board.get_at(*self.pts[4]))
        self.assert_hval_is(len2hval(3))
        self.assert_pt_has_nb_groups(1, 1)
        self.assert_pt_has_nb_groups(2, 1)
        self.assert_pt_has_nb_groups(3, 1)
        self.assert_pt_has_nb_groups(5, 0)
        self.assert_pt_group_has_len(1, nth_group=0, length=3)
        self.assert_pt_group_has_len(2, nth_group=0, length=3)
        self.assert_pt_group_has_len(3, nth_group=0, length=3)

    def test_del_at_5_3(self):
        self.put_nth(1)
        self.put_nth(2)
        self.put_nth(3)
        self.put_nth(4)
        self.put_nth(5)

        self.del_nth(3) # [1 2 _ 4 5]
        self.assertFalse(self.board.get_at(*self.pts[3]))
        self.assert_hval_is(len2hval(2) * 2)
        self.assert_pt_has_nb_groups(1, 1)
        self.assert_pt_has_nb_groups(2, 1)
        self.assert_pt_has_nb_groups(4, 1)
        self.assert_pt_has_nb_groups(5, 1)
        self.assert_pt_group_has_len(1, nth_group=0, length=2)
        self.assert_pt_group_has_len(2, nth_group=0, length=2)
        self.assert_pt_group_has_len(4, nth_group=0, length=2)
        self.assert_pt_group_has_len(5, nth_group=0, length=2)

_grouptest_base = TestBoardModel_WithAddingInDiagonalUp

class TestBoardModel_WithAddingInDiagonalDown(_grouptest_base):
    def setUp(self):
        self.pts = (
            None, # dummy
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
        )
        self.board = Board()

class TestBoardModel_WithAddingInHorizontal(_grouptest_base):
    def setUp(self):
        self.pts = (
            None, # dummy
            (1, 0),
            (2, 0),
            (3, 0),
            (4, 0),
            (5, 0),
        )
        self.board = Board()

class TestBoardModel_WithAddingInVertical(_grouptest_base):
    def setUp(self):
        self.pts = (
            None, # dummy
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
        )
        self.board = Board()

del _grouptest_base

