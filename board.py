""" board.py

    Contains the central object of Gomoku game -- the board.
"""

from model import (BOARD_SIZE, SmallSet, PLAYER_COUNT, make_chess_space,
                   make_neighbours, make_larger_neighbours)
from pieces import Piece, merge_dual, PieceGroupManager, HVALTAB

class Board(object):
    def __init__(self):
        self.size = BOARD_SIZE
        self.space = make_chess_space(19)
        # owning piece-groups for each player.
        self.piece_groups = [PieceGroupManager(len(HVALTAB) - 1)
                             for _ in xrange(PLAYER_COUNT)]
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
        piece = Piece(x, y, player)
        self.space[y][x] = piece
        for neighbour in self.find_mergeable_neighbours(piece):
            merge_dual(self, piece, neighbour)
        self.add_possible_move(x, y)
        return piece

    def add_piece_group(self, group):
        self.piece_groups[group.get_owner().pid].put(group)

    def del_piece_group(self, group):
        self.piece_groups[group.get_owner().pid].remove(group)

    def get_piece_groups(self):
        return self.piece_groups

    def add_possible_move(self, x, y):
        pm = self.possible_moves
        pm.del_at(x, y)
        for (nx, ny) in make_neighbours(x, y):
        #for (nx, ny) in make_larger_neighbours(x, y):
            if self.get_at(nx, ny) is None:
                pm.put_at(nx, ny)

    def get_possible_moves(self):
        return self.possible_moves

    def set_possible_moves(self, pmoves):
        self.possible_moves = pmoves

    def find_mergeable_neighbours(self, piece):
        res = []
        for (nx, ny) in make_neighbours(piece.x, piece.y):
            neighbour = self.get_at(nx, ny)
            if neighbour and neighbour.owner is piece.owner:
                res.append(neighbour)
        return res

