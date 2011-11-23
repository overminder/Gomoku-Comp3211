
class Future(object):
    def __init__(self, board, player):
        self.board = board
        self.player = player
        self.move = None

    def naive_minimax(self, depth, mover):
        from gamemodel import PLAYER_COUNT
        best_value = 0
        best_move = None
        if depth == 0:
            # base case -- just get the heuristic value
            self_hval = self.board.get_hval(self.player.pid)
            other_hvals = [self.board.get_hval(pid)
                           for pid in xrange(PLAYER_COUNT)
                           if pid != self.player.pid]
            other_hval = 0
            for hval in other_hvals:
                other_hval += hval
            return self_hval - 2 * other_hval

        elif mover is self.player: # max
            saved_pmoves = self.board.get_possible_moves()
            pm_iter = saved_pmoves.get_iterator()
            while pm_iter.has_next():
                (x, y) = pm_iter.get_next()
                self.board.set_possible_moves(saved_pmoves.make_copy())
                self.board.put_at(x, y, mover)
                next_future = Future(self.board, self.player)
                future_value = next_future.naive_minimax(
                        depth - 1, mover.get_next())
                if best_move is None or future_value > best_value:
                    best_value = future_value
                    best_move = [x, y]
                self.board.del_at(x, y) # Restore the board.
            self.board.set_possible_moves(saved_pmoves)
            self.move = best_move
            return best_value
        else: # min
            saved_pmoves = self.board.get_possible_moves()
            pm_iter = saved_pmoves.get_iterator()
            while pm_iter.has_next():
                (x, y) = pm_iter.get_next()
                self.board.set_possible_moves(saved_pmoves.make_copy())
                self.board.put_at(x, y, mover)
                next_future = Future(self.board, self.player)
                future_value = next_future.naive_minimax(
                        depth - 1, mover.get_next())
                if best_move is None or future_value < best_value:
                    best_value = future_value
                    best_move = [x, y]
                self.board.del_at(x, y) # Restore the board.
            self.board.set_possible_moves(saved_pmoves)
            self.move = best_move
            return best_value

