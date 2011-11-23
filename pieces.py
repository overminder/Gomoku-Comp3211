""" pieces.py
    
    Manages groups of pieces.
    When a new piece is added into the board, the board will first
    mutate its chess space (Board.put_at), find all of its neighbours
    and call pieces.merge_dual(board, new, neighbour) -- this may
    cause a brand new large final piecegroup to be constructed.

    merge_dual(b, new, old) basically does the following things.
    Firstly merge new and old into a 2-element group, whose type's
    based on the relative position of new and old.
    Then we can look ahead to the side of new and old (from which could
    be identifid in the merge->group phase), and try to merge them into
    the new group. After a merge, there is a high possibility that the
    look ahead is contained in two identical groups G_a and G_b, where
    G_a is the old group and G_b is the group that we have just constructed.
    Then, disband G_a.

    Group.merge(board, piece) will just extend itself by one and continue
    to look ahead, without doing cleanups.

    E.g., insert 1, 2, 3
    1 :- no neighbour
    3 :- no neighbour
    2 :- [1, 3], merge_dual(2, 1) ->
"""

class Piece(object):
    def __init__(self, x, y, owner):
        self.x = x
        self.y = y
        self.groups = []
        self.owner = owner

    def __repr__(self):
        return '<piece (%s %s %s) %s>' % (self.x, self.y, self.owner,
                                          self.groups)


class PieceGroup(object):
    #          0x 1x 2x 3x  4x   5x     6x     7x     8x
    HVALTAB = (0, 0, 4, 45, 999, 99999, 99999, 99999, 99999)

    def __init__(self):
        self.pieces = []

    def __len__(self):
        return len(self.pieces)

    @property
    def hval(self):
        return self.HVALTAB[len(self)]

    @property
    def min_x(self):
        return min(pc.x for pc in self.pieces)

    @property
    def min_y(self):
        return min(pc.y for pc in self.pieces)

    def add(self, piece):
        self.pieces.append(piece)
        piece.groups.append(self)

    def remove(self, piece):
        raise NotImplementedError

    def merge(self, board, piece):
        raise NotImplementedError

    def disband(self):
        hval = self.hval
        for piece in self.pieces:
            piece.groups.remove(self)
        return -hval

    def is_superset_of(self, group):
        raise NotImplementedError

class DiagonalUp(PieceGroup):
    ' / '
    def __init__(self):
        super(DiagonalUp, self).__init__()

    def __repr__(self):
        return '<piece-group(/) %d @0x%x>' % (len(self), hash(self))

    def remove(self, piece):
        old_hval = self.hval
        new_hval = 0
        left_pieces = [p for p in self.pieces if p.x < piece.x]
        rite_pieces = [p for p in self.pieces if p.x > piece.x]

        for left_piece in left_pieces:
            left_piece.groups.remove(self)
        if len(left_pieces) > 1: # Necessary to make a new group.
            left_group = DiagonalUp()
            for left_piece in left_pieces:
                left_group.add(left_piece)
            new_hval += left_group.hval

        for rite_piece in rite_pieces:
            rite_piece.groups.remove(self)
        if len(rite_pieces) > 1: # Necessary to make a new group.
            rite_group = DiagonalUp()
            for rite_piece in rite_pieces:
                rite_group.add(rite_piece)
            new_hval += rite_group.hval
        return new_hval - old_hval

    def merge(self, board, piece):
        old_hval = self.hval
        self_len = len(self)
        min_x = self.min_x
        min_y = self.min_y

        if piece.x == min_x - 1 and piece.y == min_y + self_len:
            # piece -v ./
            self.add(piece)
            look_ahead = board.get_at(piece.x - 1, piece.y + 1)
        elif piece.x == min_x + self_len and piece.y == min_y - 1:
            # / ^- piece
            self.add(piece)
            look_ahead = board.get_at(piece.x + 1, piece.y - 1)
        else:
            # Cannot merge.
            return 0

        new_hval = self.hval # After merge
        change_in_hval = 0
        if look_ahead and look_ahead.owner is piece.owner:
            change_in_hval += self.merge(board, look_ahead)
            # could go on merging containing group.
            for group in look_ahead.groups:
                if self.is_superset_of(group):
                    change_in_hval += group.disband()
        return new_hval - old_hval + change_in_hval

    def is_superset_of(self, the_other):
        if self is not the_other and isinstance(the_other, DiagonalUp):
            p1 = self.pieces[0]
            p2 = the_other.pieces[0]
            self_min_x = self.min_x
            other_min_x = the_other.min_x
            return (
                p1.y - p2.y == p2.x - p1.x and # dy/dx == -1
                self_min_x <= other_min_x and
                self_min_x + len(self) >= other_min_x + len(the_other)
            )
        return False


def merge_dual(board, new, old):
    owner = new.owner
    if new.x < old.x and new.y < old.y: # new -> \ 
        look_ahead_1 = (new.x - 1, new.y - 1)
        look_ahead_2 = (old.x + 1, old.y + 1)
        new_group = DiagonalDown()
    elif new.x < old.x and new.y > old.y: # new -> /
        look_ahead_1 = (new.x - 1, new.y + 1)
        look_ahead_2 = (old.x + 1, old.y - 1)
        new_group = DiagonalUp()
    elif new.x < old.x and new.y == old.y: # new -> -
        look_ahead_1 = (new.x - 1, new.y)
        look_ahead_2 = (old.x + 1, old.y)
        new_group = Horizontal()
    elif new.x == old.x and new.y > old.y: # new -^ |
        look_ahead_1 = (new.x, new.y - 1)
        look_ahead_2 = (old.x, old.y + 1)
        new_group = Vertical()
    else:
        return merge_dual(board, old, new) # flip.
    new_group.add(new)
    new_group.add(old)

    # try to merge ahead.
    change_in_hval = new_group.hval
    for la_piece in (board.get_at(*look_ahead_1),
                     board.get_at(*look_ahead_2)):
        if la_piece and la_piece.owner is owner:
            change_in_hval += new_group.merge(board, la_piece)
            for group in la_piece.groups[:]:
                if new_group.is_superset_of(group):
                    change_in_hval += group.disband()
    return change_in_hval

