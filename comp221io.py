""" comp221io.py

    Utility functions for input and output for fulfilling COMP221
    project assignment.

    Does monkey patch the future class to do the output.
"""

import sys
from pypy.rlib.streamio import open_file_as_stream
from pypy.rlib.parsing.makepackrat import (PackratParser, Status,
        BacktrackException)
from model import Player, PLAYER_COUNT
from board import Board
from ai import Future

# And monkey-patching Future class
def monkey_patch_future_class():
    old_init = Future.__init__
    old_eval = Future.heuristic_eval

    def new_init(self, board, player):
        old_init(self, board, player)
        self.value = -1
        self.children = []

    def new_alphabeta(self, depth, alpha, beta, mover):
        if depth == 0:
            # leaf reached -- just get the heuristic value
            return self.heuristic_eval()
        elif self.board.get_piece_groups()[mover.get_prev().pid].count_of(5):
            # ending case -- someone is winning here.
            return self.heuristic_eval()

        # prepare for searching
        saved_pmoves = self.board.get_possible_moves()
        pm_iter = saved_pmoves.get_iterator()

        if mover is self.player: # max move
            while pm_iter.has_next():
                (x, y) = pm_iter.get_next()
                self.board.set_possible_moves(saved_pmoves.make_copy())
                self.board.put_at(x, y, mover)
                next_future = Future(self.board, self.player)
                self.children.append((x, y, next_future)) # Record
                future_value = next_future.alphabeta_3p(depth - 1,
                        alpha, beta, mover.get_next())
                self.board.del_at(x, y) # Restore the board.
                if future_value > alpha:
                    alpha = future_value
                    self.move = [x, y]
                if beta <= alpha:
                    self.children.append((x, y, None)) # record prune
                    break
            self.board.set_possible_moves(saved_pmoves)
            self.value = alpha
            return alpha
        elif mover is self.player.get_next():
            # the first min move, just brute through
            while pm_iter.has_next():
                (x, y) = pm_iter.get_next()
                self.board.set_possible_moves(saved_pmoves.make_copy())
                self.board.put_at(x, y, mover)
                next_future = Future(self.board, self.player)
                self.children.append((x, y, next_future)) # Record
                future_value = next_future.alphabeta_3p(depth - 1,
                        alpha, beta, mover.get_next())
                self.board.del_at(x, y) # Restore the board.
                if future_value < beta:
                    beta = future_value
                    self.move = [x, y]
            self.board.set_possible_moves(saved_pmoves)
            self.value = beta
            return beta
        else: # the second min move, can prune
            while pm_iter.has_next():
                (x, y) = pm_iter.get_next()
                self.board.set_possible_moves(saved_pmoves.make_copy())
                self.board.put_at(x, y, mover)
                next_future = Future(self.board, self.player)
                self.children.append((x, y, next_future)) # Record
                future_value = next_future.alphabeta_3p(depth - 1,
                        alpha, beta, mover.get_next())
                self.board.del_at(x, y) # Restore the board.
                if future_value < beta:
                    beta = future_value
                    self.move = [x, y]
                if beta <= alpha:
                    self.children.append((x, y, None)) # record prune
                    break
            self.board.set_possible_moves(saved_pmoves)
            self.value = beta
            return beta

    def new_eval(self):
        retval = old_eval(self)
        self.value = retval
        return retval

    def _dump(self, prefix):
        print '%s, %d' % (prefix, self.value)
        if not self.children:
            return
        buf = []
        for x, y, child in self.children:
            if not child:
                buf.append('[pruned]')
            else:
                buf.append('[(%d,%d),%d]' % (x, y, child.value))
        print ('%s:' % prefix), (', '.join(buf))
        for x, y, child in self.children:
            if not child:
                print '[pruned] Any child after <%s, (%d,%d)> is pruned' % (
                        prefix, x, y)
            else:
                child._dump(prefix + ', (%d,%d)' % (x, y))

    def dump(self):
        x, y = self.move
        print '%s to play (%d, %d)' % (self.player.name, x, y)
        print 'Search tree:'
        self._dump('root')

    Future.__init__ = new_init
    Future.alphabeta_3p = new_alphabeta
    Future.heuristic_eval = new_eval
    Future.dump = dump
    Future._dump = _dump

monkey_patch_future_class()


class TupleParser(PackratParser):
    r'''
    IGNORE:
        `[ \t\n\r]`;
    LPAREN:
        IGNORE*
        '(';
    RPAREN:
        IGNORE*
        ')';
    COMMA:
        IGNORE*
        ',';
    NUMBER:
        IGNORE*
        num = `[0-9]+`
        return {num};

    goal:
        c = tuple_list
        return {c}
      | '0'
        return {[]};

    tuple_list:
        c1 = (
            tuple
            [COMMA]
        )*
        c2 = tuple
        return {c1 + [c2]};

    tuple:
        LPAREN
        fst = NUMBER
        COMMA
        snd = NUMBER
        RPAREN
        return {[fst, snd]};
    '''
    packrat_using_default_init = True

def load_game(filename):
    f = open_file_as_stream(filename, 'r')
    content = f.readall().strip('\n')
    line0, line1 = content.split('\n')
    player =  Player.cache[int(line0)]
    moves = TupleParser(line1).goal()
    board = Board()
    
    for i in xrange(len(moves)): # enumerate sometimes will fail...
        x, y = moves[i]
        p = Player.cache[i % PLAYER_COUNT]
        board.put_at(int(x), int(y), p)
    return player, board

