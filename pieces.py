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
"""

# Only for those that are not totally blocked.
#          0x 1x 2x 3x  4x  5x     6x      7x       8x
HVALTAB = [0, 0, 4, 15, 35, 99999, 999999, 9999999, 99999999]
# for 2(2x) -> 2(3x) but not 3x->4x, 2(3x - 2x) > 4x - 3x

HVALTAB2 = [
    [0, 0, 8, 600, 9999, 99999, 999999, 9999999, 99999999], # blockade 0
    [0, 0, 4, 15,  600,  99999, 999999, 9999999, 99999999], # blockade 1
    [0, 0, 0,  0,    0,  99999, 999999, 9999999, 99999999], # blockade 2
]

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

    def __init__(self):
        self.pieces = []

    def get_length(self):
        return len(self.pieces)

    def get_hval(self):
        return HVALTAB[self.get_length()]

    def get_min_x(self):
        # pypy work around..
        min_x = self.pieces[0].x
        for pc in self.pieces:
            if pc.x < min_x:
                min_x = pc.x
        return min_x

    def get_min_y(self):
        # pypy work around..
        min_y = self.pieces[0].y
        for pc in self.pieces:
            if pc.y < min_y:
                min_y = pc.y
        return min_y

    def get_max_x(self):
        # pypy work around..
        max_x = self.pieces[0].x
        for pc in self.pieces:
            if pc.x > max_x:
                max_x = pc.x
        return max_x

    def get_max_y(self):
        # pypy work around..
        max_y = self.pieces[0].y
        for pc in self.pieces:
            if pc.y > max_y:
                max_y = pc.y
        return max_y

    def get_owner(self):
        return self.pieces[0].owner

    def add(self, piece):
        self.pieces.append(piece)
        piece.groups.append(self)

    def remove(self, board, piece):
        raise NotImplementedError

    def merge(self, board, piece):
        raise NotImplementedError

    def disband(self, board):
        board.del_piece_group(self)
        for piece in self.pieces:
            piece.groups.remove(self)

    def is_superset_of(self, group):
        raise NotImplementedError

    def heuristic_eval(self, board):
        raise NotImplementedError


class GroupWithChangeInX(PieceGroup):
    """ Those three groups (\\) (-) (/) can share the same remove method. """
    def __init__(self):
        #super(GroupWithChangeInX, self).__init__()
        PieceGroup.__init__(self) # workaround.

    def remove(self, board, piece):
        board.del_piece_group(self)
        left_pieces = [p for p in self.pieces if p.x < piece.x]
        rite_pieces = [p for p in self.pieces if p.x > piece.x]

        for left_piece in left_pieces:
            left_piece.groups.remove(self)
        if len(left_pieces) > 1: # Necessary to make a new group.
            left_group = self.__class__()
            for left_piece in left_pieces:
                left_group.add(left_piece)
            board.add_piece_group(left_group)

        for rite_piece in rite_pieces:
            rite_piece.groups.remove(self)
        if len(rite_pieces) > 1: # Necessary to make a new group.
            rite_group = self.__class__()
            for rite_piece in rite_pieces:
                rite_group.add(rite_piece)
            board.add_piece_group(rite_group)


class DiagonalUp(GroupWithChangeInX):
    ' / '
    def __init__(self):
        #super(DiagonalUp, self).__init__()
        GroupWithChangeInX.__init__(self) # workaround.

    def __repr__(self):
        return '<piece-group(/) %d @0x%x>' % (len(self), hash(self))

    def merge(self, board, piece):
        self_len = self.get_length()
        min_x = self.get_min_x()
        min_y = self.get_min_y()

        if piece.x == min_x - 1 and piece.y == min_y + self_len:
            board.del_piece_group(self)
            # piece -v ./
            self.add(piece)
            look_ahead = board.get_at(piece.x - 1, piece.y + 1)
        elif piece.x == min_x + self_len and piece.y == min_y - 1:
            board.del_piece_group(self)
            # / ^- piece
            self.add(piece)
            look_ahead = board.get_at(piece.x + 1, piece.y - 1)
        else:
            # Cannot merge.
            return

        board.add_piece_group(self)
        if look_ahead and look_ahead.owner is piece.owner:
            self.merge(board, look_ahead)
            # could go on merging containing group.
            for group in look_ahead.groups:
                if self.is_superset_of(group):
                    group.disband(board)

    def is_superset_of(self, the_other):
        if self is not the_other and isinstance(the_other, DiagonalUp):
            p1 = self.pieces[0]
            p2 = the_other.pieces[0]
            self_min_x = self.get_min_x()
            other_min_x = the_other.get_min_x()
            return (
                p1.y - p2.y == p2.x - p1.x and # dy/dx == -1
                self_min_x <= other_min_x and
                self_min_x + self.get_length() >=
                    other_min_x + the_other.get_length()
            )
        return False

    def heuristic_eval(self, board):
        blockage = 0
        self_len = self.get_length()
        min_x = self.get_min_x()
        max_y = self.get_max_y()

        left_pt = (min_x - 1, max_y + 1)
        if not board.pos_is_valid(*left_pt) or board.get_at(*left_pt):
            blockage += 1

        rite_pt = (min_x + self_len, max_y + self_len)
        if not board.pos_is_valid(*rite_pt) or board.get_at(*rite_pt):
            blockage += 1
        return HVALTAB2[blockage][self_len]


class DiagonalDown(GroupWithChangeInX):
    ' \ '
    def __init__(self):
        #super(DiagonalDown, self).__init__()
        GroupWithChangeInX.__init__(self) # workaround.

    def __repr__(self):
        return '<piece-group(\\) %d @0x%x>' % (len(self), hash(self))

    def merge(self, board, piece):
        self_len = self.get_length()
        self_len += 0
        min_x = self.get_min_x()
        min_y = self.get_min_y()

        if piece.x == min_x - 1 and piece.y == min_y - 1:
            board.del_piece_group(self)
            # piece -^ \
            self.add(piece)
            look_ahead = board.get_at(piece.x - 1, piece.y - 1)
        elif piece.x == min_x + self_len and piece.y == min_y + self_len:
            board.del_piece_group(self)
            # \ v- piece
            self.add(piece)
            look_ahead = board.get_at(piece.x + 1, piece.y + 1)
        else:
            # Cannot merge.
            return

        board.add_piece_group(self)
        if look_ahead and look_ahead.owner is piece.owner:
            self.merge(board, look_ahead)
            # could go on merging containing group.
            for group in look_ahead.groups:
                if self.is_superset_of(group):
                    group.disband(board)

    def is_superset_of(self, the_other):
        if self is not the_other and isinstance(the_other, DiagonalDown):
            p1 = self.pieces[0]
            p2 = the_other.pieces[0]
            self_min_x = self.get_min_x()
            other_min_x = the_other.get_min_x()
            return (
                p1.y - p2.y == p1.x - p2.x and # dy/dx == 1
                self_min_x <= other_min_x and
                self_min_x + self.get_length() >=
                    other_min_x + the_other.get_length()
            )
        return False

    def heuristic_eval(self, board):
        blockage = 0
        self_len = self.get_length()
        min_x = self.get_min_x()
        min_y = self.get_min_y()

        left_pt = (min_x - 1, min_y - 1)
        if not board.pos_is_valid(*left_pt) or board.get_at(*left_pt):
            blockage += 1

        rite_pt = (min_x + self_len, min_y + self_len)
        if not board.pos_is_valid(*rite_pt) or board.get_at(*rite_pt):
            blockage += 1
        return HVALTAB2[blockage][self_len]


class Horizontal(GroupWithChangeInX):
    ' - '
    def __init__(self):
        GroupWithChangeInX.__init__(self) # workaround for pypy
        #super(Horizontal, self).__init__()

    def __repr__(self):
        return '<piece-group(-) %d @0x%x>' % (len(self), hash(self))

    def merge(self, board, piece):
        self_len = self.get_length()
        min_x = self.get_min_x()
        min_y = self.get_min_y()

        if piece.x == min_x - 1 and piece.y == min_y:
            board.del_piece_group(self)
            # piece -> -
            self.add(piece)
            look_ahead = board.get_at(piece.x - 1, piece.y)
        elif piece.x == min_x + self_len and piece.y == min_y:
            board.del_piece_group(self)
            # \ v- piece
            self.add(piece)
            look_ahead = board.get_at(piece.x + 1, piece.y)
        else:
            # Cannot merge.
            return

        board.add_piece_group(self)
        if look_ahead and look_ahead.owner is piece.owner:
            self.merge(board, look_ahead)
            # could go on merging containing group.
            for group in look_ahead.groups:
                if self.is_superset_of(group):
                    group.disband(board)

    def is_superset_of(self, the_other):
        if self is not the_other and isinstance(the_other, Horizontal):
            p1 = self.pieces[0]
            p2 = the_other.pieces[0]
            self_min_x = self.get_min_x()
            other_min_x = the_other.get_min_x()
            return (
                p1.y == p2.y and
                self_min_x <= other_min_x and
                self_min_x + self.get_length() >=
                    other_min_x + the_other.get_length()
            )
        return False

    def heuristic_eval(self, board):
        blockage = 0
        self_len = self.get_length()
        min_x = self.get_min_x()
        my_y = self.get_min_y()

        left_pt = (min_x - 1, my_y)
        if not board.pos_is_valid(*left_pt) or board.get_at(*left_pt):
            blockage += 1

        rite_pt = (min_x + self_len, my_y)
        if not board.pos_is_valid(*rite_pt) or board.get_at(*rite_pt):
            blockage += 1
        return HVALTAB2[blockage][self_len]


class GroupWithChangeInY(PieceGroup):
    """ This group (|) has a different remove method. """
    def __init__(self):
        #super(GroupWithChangeInY, self).__init__()
        PieceGroup.__init__(self) # workaround.

    def remove(self, board, piece):
        board.del_piece_group(self)
        top_pieces = [p for p in self.pieces if p.y < piece.y]
        bottom_pieces = [p for p in self.pieces if p.y > piece.y]

        for top_piece in top_pieces:
            top_piece.groups.remove(self)
        if len(top_pieces) > 1: # Necessary to make a new group.
            top_group = self.__class__()
            for top_piece in top_pieces:
                top_group.add(top_piece)
            board.add_piece_group(top_group)

        for bottom_piece in bottom_pieces:
            bottom_piece.groups.remove(self)
        if len(bottom_pieces) > 1: # Necessary to make a new group.
            bottom_group = self.__class__()
            for bottom_piece in bottom_pieces:
                bottom_group.add(bottom_piece)
            board.add_piece_group(bottom_group)

class Vertical(GroupWithChangeInY):
    ' - '
    def __init__(self):
        #super(Vertical, self).__init__()
        GroupWithChangeInY.__init__(self) # workaround.

    def __repr__(self):
        return '<piece-group(-) %d @0x%x>' % (len(self), hash(self))

    def merge(self, board, piece):
        self_len = self.get_length()
        self_len += 0
        min_x = self.get_min_x()
        min_y = self.get_min_y()

        if piece.x == min_x and piece.y == min_y - 1:
            board.del_piece_group(self)
            # piece -> -
            self.add(piece)
            look_ahead = board.get_at(piece.x, piece.y - 1)
        elif piece.x == min_x and piece.y == min_y + self_len:
            board.del_piece_group(self)
            # \ v- piece
            self.add(piece)
            look_ahead = board.get_at(piece.x, piece.y + 1)
        else:
            # Cannot merge.
            return

        board.add_piece_group(self)
        if look_ahead and look_ahead.owner is piece.owner:
            self.merge(board, look_ahead)
            # could go on merging containing group.
            for group in look_ahead.groups:
                if self.is_superset_of(group):
                    group.disband(board)

    def is_superset_of(self, the_other):
        if self is not the_other and isinstance(the_other, Vertical):
            p1 = self.pieces[0]
            p2 = the_other.pieces[0]
            self_min_y = self.get_min_y()
            other_min_y = the_other.get_min_y()
            return (
                p1.x == p2.x and
                self_min_y <= other_min_y and
                self_min_y + self.get_length() >=
                    other_min_y + the_other.get_length()
            )
        return False

    def heuristic_eval(self, board):
        blockage = 0
        self_len = self.get_length()
        my_x = self.get_min_x()
        min_y = self.get_min_y()

        upper_pt = (my_x, min_y - 1)
        if not board.pos_is_valid(*upper_pt) or board.get_at(*upper_pt):
            blockage += 1

        lower_pt = (my_x, min_y + self_len)
        if not board.pos_is_valid(*lower_pt) or board.get_at(*lower_pt):
            blockage += 1
        return HVALTAB2[blockage][self_len]

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
    elif new.x == old.x and new.y < old.y: # new -^ |
        look_ahead_1 = (new.x, new.y - 1)
        look_ahead_2 = (old.x, old.y + 1)
        new_group = Vertical()
    else:
        return merge_dual(board, old, new) # flip.
    new_group.add(new)
    new_group.add(old)
    board.add_piece_group(new_group)

    # try to merge ahead. XXX: pypy hack to use list
    piece1, piece2 = board.get_at(*look_ahead_1), board.get_at(*look_ahead_2)
    for la_piece in [piece1, piece2]:
        if la_piece and la_piece.owner is owner:
            new_group.merge(board, la_piece)
            for group in la_piece.groups[:]:
                if new_group.is_superset_of(group):
                    group.disband(board)


class PieceGroupManager(object):
    def __init__(self, piece_lengths):
        self._groups = [[] for _ in xrange(piece_lengths + 1)]

    def put(self, piece):
        self._groups[piece.get_length()].append(piece)

    def remove(self, piece):
        self._groups[piece.get_length()].remove(piece)

    def count_of(self, len_spec):
        return len(self._groups[len_spec])

    def get_groups(self):
        return self._groups


