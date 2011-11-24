
from time import time
from random import random as py_random
import __pypy_path__
from pypy.rlib.objectmodel import we_are_translated
from pypy.rlib.rrandom import Random
_random = Random()

def random():
    if we_are_translated():
        return _random.random()
    else:
        return py_random()

class ObjSpace(object):
    def __init__(self, depth, nb_children, node_class):
        self.expansion_count = 0
        self.tree_depth = depth
        self.nb_children = nb_children
        self.magnitude = 10 ** 6
        self.node_class = node_class
        self.next_node_id = 0
        self.root = None

    def gen_rand_value(self):
        return (random() - 0.5) * self.magnitude

    def gen_node_id(self):
        self.next_node_id += 1
        return self.next_node_id

    def make_node(self):
        return self.node_class(self, self.gen_rand_value())

    def populate(self):
        self.root = self.make_node()
        self._populate_node(self.tree_depth, self.root)

    def _populate_node(self, depth, node):
        if depth == 0:
            return
        else:
            for i in xrange(int(self.nb_children * random()) + 1):
                child = self.make_node()
                node.put(child)
                self._populate_node(depth - 1, child)

    def record_expansion(self):
        self.expansion_count += 1

class Node(object):
    def __init__(self, space, value):
        self.children = []
        self.value = value
        self.nid = space.gen_node_id()
        self.parent = None

    def to_string(self):
        return '<node(%d) %s>' % (self.nid, self.value)

    def put(self, child):
        self.children.append(child)
        child.parent = self

    def get_value(self, space):
        """ Hook to record this.
        """
        space.record_expansion()
        sum_up = 0
        while self:
            sum_up += self.value
            self = self.parent
        return sum_up

class Future(object):
    def __init__(self, space, tree, player):
        self.space = space
        self.tree = tree
        self.player = player
        self.future = None

    def to_string(self):
        return '<future value=%s>' % self.get_value()

    def get_value(self):
        return self.tree.get_value(self.space)

    def get_leaf(self):
        while self.future:
            self = self.future
        return self

    def minimax(self, depth, player):
        if depth == 0:
            return self.get_value()
        elif player is self.player: # max
            curr_max = -(1 << 61)
            for child in self.tree.children:
                future = Future(self.space, child, self.player)
                hval = future.minimax(depth - 1, player.get_next())
                if hval > curr_max:
                    curr_max = hval
                    self.future = future
            return curr_max
        else: # min
            curr_min = 1 << 61
            for child in self.tree.children:
                future = Future(self.space, child, self.player)
                hval = future.minimax(depth - 1, player.get_next())
                if hval < curr_min:
                    curr_min = hval
                    self.future = future
            return curr_min


    def alphabeta(self, depth, alpha, beta, player):
        if depth == 0:
            return self.get_value()
        elif player is self.player: # max
            for child in self.tree.children:
                future = Future(self.space, child, self.player)
                future_value = future.alphabeta(depth - 1, alpha, beta,
                                                player.get_next())
                if future_value > alpha:
                    alpha = future_value
                    self.future = future
                if beta <= alpha:
                    break
            return alpha
        else: # min
            for child in self.tree.children:
                future = Future(self.space, child, self.player)
                future_value = future.alphabeta(depth - 1, alpha, beta,
                                                player.get_next())
                if future_value < beta:
                    beta = future_value
                    self.future = future
                if beta <= alpha:
                    break
            self.future = future
            return beta

class Player(object):
    pass

class PlayerOne(Player):
    def get_next(self):
        return player_two

class PlayerTwo(Player):
    def get_next(self):
        return player_one

player_one = PlayerOne()
player_two = PlayerTwo()

def main(argv):
    try:
        depth = int(argv[1])
    except (IndexError, ValueError):
        depth = 5
    try:
        nb_children = int(argv[2])
    except (IndexError, ValueError):
        nb_children = 10

    space = ObjSpace(depth=depth, nb_children=nb_children, node_class=Node)
    populate_start = time()
    print '[Populating] dept => %s, nb_children => %s' % (depth, nb_children)
    space.populate()
    populate_time = time() - populate_start
    print '[Populating] time-used => %s' % populate_time

    future_naive = Future(space, space.root, player_one)
    naive_start = time()
    naive_value = future_naive.minimax(depth, player_one)
    naive_time = time() - naive_start
    naive_count = space.expansion_count

    space.expansion_count = 0
    future_ab = Future(space, space.root, player_one)
    ab_start = time()
    ab_value = future_ab.alphabeta(depth, -(1 << 61), (1 << 61), player_one)
    ab_time = time() - ab_start
    ab_count = space.expansion_count

    print '[Naive] value => %s, count => %s' % (naive_value, naive_count)
    print '[Naive] time-used => %s' % naive_time
    print '[Naive] leaf => %s' % future_naive.get_leaf().to_string()

    # XXX: sometimes the value of future_ab is larger than that of naive..
    print '[Prune] value => %s, count => %s' % (ab_value, ab_count)
    print '[Prune] time-used => %s' % ab_time
    print '[Naive] leaf => %s' % future_ab.get_leaf().to_string()

if __name__ == '__main__':
    import sys
    main(sys.argv)

