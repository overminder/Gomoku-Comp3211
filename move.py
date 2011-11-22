""" move.py
    Instances of Move fill up the board, while constructing useful
    information about their groups, which could be used to evaluate
    the heuristic value in a fast way.
"""

def merge_dual(board, new_move, old_move):
    """ Merge new_move with old_move.
        new_move is fresh but may already be inside some groups.
    """
    if new_move.x < old_move.x and new_move.y < old_move.y:
        # new -> \
        new_group = DiagonalDown()
    elif new_move.x < old_move.x and new_move.y > old_move.y:
        # new -> / 
        new_group = DiagonalUp()
    elif new_move.x == old_move.x and new_move.y > old_move.y:
        # | v- new
        new_group = Vertical()
    elif new_move.x < old_move.x and new_move.y == old_move.y:
        # new -> -
        new_group = Horizontal()
    else: # swap.
        return merge_dual(board, old_move, new_move)
    new_group.add_move(old_move)
    new_group.add_move(new_move)
    # XXX: reduce look-ahead from 8 to 1?
    change_in_hval = new_group.heuristic_value
    for look_ahead in board.mergeables_of(new_move):
        change_in_hval += new_group.try_merge_move(board, look_ahead)
        for group in look_ahead.belongs_to[:]:
            if new_group.is_superset_of(group):
                # Merge smaller group
                change_in_hval += new_group.merge_with_group(group)

    # Note that on the other side there may also have some things to merge.
    for look_ahead in board.mergeables_of(old_move):
        change_in_hval += new_group.try_merge_move(board, look_ahead)
        for group in look_ahead.belongs_to[:]:
            if new_group.is_superset_of(group):
                # Merge smaller group
                change_in_hval += new_group.merge_with_group(group)
    return change_in_hval


class Move(object):
    def __init__(self, x, y, player):
        self.x = x
        self.y = y
        self.player = player
        self.belongs_to = []

    def __repr__(self):
        return '<move (%s, %s, %s)>' % (self.x, self.y, self.player.name)

class Group(object):
    def __init__(self):
        self.moves = []
        #self.min_x = None
        #self.min_y = None

    @property
    def min_x(self):
        return min(m.x for m in self.moves)

    @property
    def min_y(self):
        return min(m.y for m in self.moves)

    def add_move(self, move):
        self.moves.append(move)
        move.belongs_to.append(self)
        #if self.min_x is None or self.min_x > move.x:
        #    self.min_x = move.x
        #if self.min_y is None or self.min_y > move.y:
        #    self.min_y = move.y

    def try_merge_move(self, board, move):
        """ Returns the change in the heuristic value.
            XXX: for other player as well?
        """
        raise NotImplementedError

    def is_superset_of(self, group):
        raise NotImplementedError

    def merge_with_group(self, group):
        hval = group.heuristic_value
        for child in group.moves:
            child.belongs_to.remove(group)
        return -hval

    @property
    def owner(self):
        return self.moves[0].player

    #                  0x 1x 2x 3x  4x   5x     6x 7x 8x 9x
    heuristic_table = (0, 1, 4, 45, 999, 99999, 0, 0, 0, 0)

    @property
    def heuristic_value(self):
        return self.heuristic_table[len(self)]

    def __len__(self):
        return len(self.moves)

class DiagonalUp(Group):
    """ / """
    def __init__(self):
        super(DiagonalUp, self).__init__()

    def __repr__(self):
        return '<group (/) %d @0x%x>' % (len(self), hash(self))

    def try_merge_move(self, board, move):
        old_value = self.heuristic_value
        self_len = len(self)
        if (move.x == self.min_x - 1 and move.y == self.min_y + self_len):
            # Successful addition, try to merge more along the way.
            self.add_move(move)
            look_ahead = board.get_at_safe(move.x - 1, move.y + 1)
        elif (move.x == self.min_x + self_len and move.y == self.min_y - 1):
            # Successful addition, try to merge more along the way.
            self.add_move(move)
            look_ahead = board.get_at_safe(move.x + 1, move.y - 1)
        else:
            return 0
        new_value = self.heuristic_value
        change_in_hval = 0
        if look_ahead and look_ahead.player is move.player:
            change_in_hval += self.try_merge_move(board, look_ahead)
            for group in look_ahead.belongs_to[:]:
                if self.is_superset_of(group):
                    # Merge smaller group
                    change_in_hval += self.merge_with_group(group)
        return new_value - old_value + change_in_hval

    def is_superset_of(self, group):
        if not isinstance(group, DiagonalUp) or self is group:
            return False
        else:
            if self.min_x <= group.min_x and (
                    self.min_x + len(self) >= group.min_x + len(group)):
                return True
            else:
                return False

class DiagonalDown(Group):
    """ \ """
    def __init__(self):
        super(DiagonalDown, self).__init__()

    def __repr__(self):
        return '<group (\\) %d @0x%x>' % (len(self), hash(self))

    def try_merge_move(self, board, move):
        old_value = self.heuristic_value
        self_len = len(self)
        if (move.x == self.min_x - 1 and move.y == self.min_y - 1):
            # Successful addition, try to merge more along the way.
            self.add_move(move)
            look_ahead = board.get_at_safe(move.x - 1, move.y - 1)
        elif (move.x == self.min_x + self_len and
                move.y == self.min_y + self_len):
            # Successful addition, try to merge more along the way.
            self.add_move(move)
            look_ahead = board.get_at_safe(move.x + 1, move.y + 1)
        else:
            return 0
        new_value = self.heuristic_value
        change_in_hval = 0
        if look_ahead and look_ahead.player is move.player:
            change_in_hval += self.try_merge_move(board, look_ahead)
            for group in look_ahead.belongs_to[:]:
                if self.is_superset_of(group):
                    # Merge smaller group
                    change_in_hval += self.merge_with_group(group)
        return new_value - old_value + change_in_hval

    def is_superset_of(self, group):
        if not isinstance(group, DiagonalDown) or self is group:
            return False
        else:
            if self.min_x <= group.min_x and (
                    self.min_x + len(self) >= group.min_x + len(group)):
                return True
            else:
                return False

class Horizontal(Group):
    """ - """
    def __init__(self):
        super(Horizontal, self).__init__()

    def __repr__(self):
        return '<group (-) %d @0x%x>' % (len(self), hash(self))

    def try_merge_move(self, board, move):
        old_value = self.heuristic_value
        self_len = len(self)
        if (move.x == self.min_x - 1 and move.y == self.min_y):
            # Successful addition, try to merge more along the way.
            self.add_move(move)
            look_ahead = board.get_at_safe(move.x - 1, move.y)
        elif (move.x == self.min_x + self_len and move.y == self.min_y):
            # Successful addition, try to merge more along the way.
            self.add_move(move)
            look_ahead = board.get_at_safe(move.x + 1, move.y)
        else:
            return 0
        new_value = self.heuristic_value
        change_in_hval = 0
        if look_ahead and look_ahead.player is move.player:
            change_in_hval += self.try_merge_move(board, look_ahead)
            for group in look_ahead.belongs_to[:]:
                if self.is_superset_of(group):
                    # Merge smaller group
                    change_in_hval += self.merge_with_group(group)
        return new_value - old_value + change_in_hval

    def is_superset_of(self, group):
        if not isinstance(group, Horizontal) or self is group:
            return False
        else:
            if self.min_x <= group.min_x and (
                    self.min_x + len(self) >= group.min_x + len(group)):
                return True
            else:
                return False

class Vertical(Group):
    """ | """
    def __init__(self):
        super(Vertical, self).__init__()

    def __repr__(self):
        return '<group (|) %d @0x%x>' % (len(self), hash(self))

    def try_merge_move(self, board, move):
        old_value = self.heuristic_value
        self_len = len(self)
        if move.x == self.min_x and move.y == self.min_y - 1:
            # Successful addition, try to merge more along the way.
            self.add_move(move)
            look_ahead = board.get_at_safe(move.x, move.y - 1)
        elif move.x == self.min_x and move.y == self.min_y + self_len:
            # Successful addition, try to merge more along the way.
            self.add_move(move)
            look_ahead = board.get_at_safe(move.x, move.y + 1)
        else:
            return 0
        new_value = self.heuristic_value
        change_in_hval = 0
        if look_ahead and look_ahead.player is move.player:
            change_in_hval += self.try_merge_move(board, look_ahead)
            for group in look_ahead.belongs_to[:]:
                if self.is_superset_of(group):
                    # Merge smaller group
                    change_in_hval += self.merge_with_group(group)
        return new_value - old_value + change_in_hval

    def is_superset_of(self, group):
        if not isinstance(group, Vertical) or self is group:
            return False
        else:
            if self.min_y <= group.min_y and (
                    self.min_y + len(self) >= group.min_y + len(group)):
                return True
            else:
                return False

