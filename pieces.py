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
    HVALTAB = [0, 0, 4, 15, 35, 99999, 999999, 9999999, 99999999]
    # for 2(2x) -> 2(3x) but not 3x->4x, 2(3x - 2x) > 4x - 3x

    def __init__(self):
        self.pieces = []

    def get_length(self):
        return len(self.pieces)

    def get_hval(self):
        return self.HVALTAB[self.get_length()]

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

    def add(self, piece):
        self.pieces.append(piece)
        piece.groups.append(self)

    def remove(self, piece):
        raise NotImplementedError

    def merge(self, board, piece):
        raise NotImplementedError

    def disband(self):
        hval = self.get_hval()
        for piece in self.pieces:
            piece.groups.remove(self)
        return -hval

    def is_superset_of(self, group):
        raise NotImplementedError

class GroupWithChangeInX(PieceGroup):
    """ Those three groups (\\) (-) (/) can share the same remove method. """
    def __init__(self):
        #super(GroupWithChangeInX, self).__init__()
        PieceGroup.__init__(self) # workaround.

    def remove(self, piece):
        old_hval = self.get_hval()
        new_hval = 0
        left_pieces = [p for p in self.pieces if p.x < piece.x]
        rite_pieces = [p for p in self.pieces if p.x > piece.x]

        for left_piece in left_pieces:
            left_piece.groups.remove(self)
        if len(left_pieces) > 1: # Necessary to make a new group.
            left_group = self.__class__()
            for left_piece in left_pieces:
                left_group.add(left_piece)
            new_hval += left_group.get_hval()

        for rite_piece in rite_pieces:
            rite_piece.groups.remove(self)
        if len(rite_pieces) > 1: # Necessary to make a new group.
            rite_group = self.__class__()
            for rite_piece in rite_pieces:
                rite_group.add(rite_piece)
            new_hval += rite_group.get_hval()
        return new_hval - old_hval


class DiagonalUp(GroupWithChangeInX):
    ' / '
    def __init__(self):
        #super(DiagonalUp, self).__init__()
        GroupWithChangeInX.__init__(self) # workaround.

    def __repr__(self):
        return '<piece-group(/) %d @0x%x>' % (len(self), hash(self))

    def merge(self, board, piece):
        old_hval = self.get_hval()
        self_len = self.get_length()
        min_x = self.get_min_x()
        min_y = self.get_min_y()

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

        new_hval = self.get_hval() # After merge
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
            self_min_x = self.get_min_x()
            other_min_x = the_other.get_min_x()
            return (
                p1.y - p2.y == p2.x - p1.x and # dy/dx == -1
                self_min_x <= other_min_x and
                self_min_x + self.get_length() >=
                    other_min_x + the_other.get_length()
            )
        return False

class DiagonalDown(GroupWithChangeInX):
    ' \ '
    def __init__(self):
        #super(DiagonalDown, self).__init__()
        GroupWithChangeInX.__init__(self) # workaround.

    def __repr__(self):
        return '<piece-group(\\) %d @0x%x>' % (len(self), hash(self))

    def merge(self, board, piece):
        old_hval = self.get_hval()
        self_len = self.get_length()
        min_x = self.get_min_x()
        min_y = self.get_min_y()

        if piece.x == min_x - 1 and piece.y == min_y - 1:
            # piece -^ \
            self.add(piece)
            look_ahead = board.get_at(piece.x - 1, piece.y - 1)
        elif piece.x == min_x + self_len and piece.y == min_y + self_len:
            # \ v- piece
            self.add(piece)
            look_ahead = board.get_at(piece.x + 1, piece.y + 1)
        else:
            # Cannot merge.
            return 0

        new_hval = self.get_hval() # After merge
        change_in_hval = 0
        if look_ahead and look_ahead.owner is piece.owner:
            change_in_hval += self.merge(board, look_ahead)
            # could go on merging containing group.
            for group in look_ahead.groups:
                if self.is_superset_of(group):
                    change_in_hval += group.disband()
        return new_hval - old_hval + change_in_hval

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

class Horizontal(GroupWithChangeInX):
    ' - '
    def __init__(self):
        GroupWithChangeInX.__init__(self) # workaround for pypy
        #super(Horizontal, self).__init__()

    def __repr__(self):
        return '<piece-group(-) %d @0x%x>' % (len(self), hash(self))

    def merge(self, board, piece):
        old_hval = self.get_hval()
        self_len = self.get_length()
        min_x = self.get_min_x()
        min_y = self.get_min_y()

        if piece.x == min_x - 1 and piece.y == min_y:
            # piece -> -
            self.add(piece)
            look_ahead = board.get_at(piece.x - 1, piece.y)
        elif piece.x == min_x + self_len and piece.y == min_y:
            # \ v- piece
            self.add(piece)
            look_ahead = board.get_at(piece.x + 1, piece.y)
        else:
            # Cannot merge.
            return 0

        new_hval = self.get_hval() # After merge
        change_in_hval = 0
        if look_ahead and look_ahead.owner is piece.owner:
            change_in_hval += self.merge(board, look_ahead)
            # could go on merging containing group.
            for group in look_ahead.groups:
                if self.is_superset_of(group):
                    change_in_hval += group.disband()
        return new_hval - old_hval + change_in_hval

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

class GroupWithChangeInY(PieceGroup):
    """ This group (|) has a different remove method. """
    def __init__(self):
        #super(GroupWithChangeInY, self).__init__()
        PieceGroup.__init__(self) # workaround.

    def remove(self, piece):
        old_hval = self.get_hval()
        new_hval = 0
        top_pieces = [p for p in self.pieces if p.y < piece.y]
        bottom_pieces = [p for p in self.pieces if p.y > piece.y]

        for top_piece in top_pieces:
            top_piece.groups.remove(self)
        if len(top_pieces) > 1: # Necessary to make a new group.
            top_group = self.__class__()
            for top_piece in top_pieces:
                top_group.add(top_piece)
            new_hval += top_group.get_hval()

        for bottom_piece in bottom_pieces:
            bottom_piece.groups.remove(self)
        if len(bottom_pieces) > 1: # Necessary to make a new group.
            bottom_group = self.__class__()
            for bottom_piece in bottom_pieces:
                bottom_group.add(bottom_piece)
            new_hval += bottom_group.get_hval()
        return new_hval - old_hval

class Vertical(GroupWithChangeInY):
    ' - '
    def __init__(self):
        #super(Vertical, self).__init__()
        GroupWithChangeInY.__init__(self) # workaround.

    def __repr__(self):
        return '<piece-group(-) %d @0x%x>' % (len(self), hash(self))

    def merge(self, board, piece):
        old_hval = self.get_hval()
        self_len = self.get_length()
        min_x = self.get_min_x()
        min_y = self.get_min_y()

        if piece.x == min_x and piece.y == min_y - 1:
            # piece -> -
            self.add(piece)
            look_ahead = board.get_at(piece.x, piece.y - 1)
        elif piece.x == min_x and piece.y == min_y + self_len:
            # \ v- piece
            self.add(piece)
            look_ahead = board.get_at(piece.x, piece.y + 1)
        else:
            # Cannot merge.
            return 0

        new_hval = self.get_hval() # After merge
        change_in_hval = 0
        if look_ahead and look_ahead.owner is piece.owner:
            change_in_hval += self.merge(board, look_ahead)
            # could go on merging containing group.
            for group in look_ahead.groups:
                if self.is_superset_of(group):
                    change_in_hval += group.disband()
        return new_hval - old_hval + change_in_hval

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

    # try to merge ahead.
    change_in_hval = new_group.get_hval()
    for la_piece in [board.get_at(*look_ahead_1),
                     board.get_at(*look_ahead_2)]:
        if la_piece and la_piece.owner is owner:
            change_in_hval += new_group.merge(board, la_piece)
            for group in la_piece.groups[:]:
                if new_group.is_superset_of(group):
                    change_in_hval += group.disband()
    return change_in_hval

